import collections
import contextlib
import sys
from argparse import ArgumentParser
from typing import Iterator

from peewee import ColumnMetadata, Database, MySQLDatabase, ProgrammingError

from cli.base import ScriptBase
from common.entities import DB
from common.model import create_all_tables
from conf import init_db, settings

TEMP_DB_NAME: str = "migration_check_tmp_db"

CheckMetadata = collections.namedtuple("CheckMetadata", ("name", "clause"))

FkRulesMetadata = collections.namedtuple("FkRulesMetadata", ("table", "column", "update_rule", "delete_rule"))


@contextlib.contextmanager
def init_temporary_db(name: str) -> MySQLDatabase:
    db_settings = settings.DATABASE
    DB.execute_sql(f"CREATE DATABASE {name}")
    try:
        database = MySQLDatabase(
            name,
            user=db_settings["user"],
            passwd=db_settings["passwd"],
            host=db_settings["host"],
            port=db_settings["port"],
        )
        create_all_tables(database)
        yield database
    finally:
        DB.execute_sql(f"DROP DATABASE {name}")


def get_check_constraints(db: Database, table_name: str) -> list[CheckMetadata]:
    sql = """
        SELECT c.constraint_name, c.check_clause
        FROM information_schema.table_constraints AS t
        INNER JOIN information_schema.check_constraints AS c
            ON t.constraint_name = c.constraint_name
                AND t.constraint_schema = c.constraint_schema
        WHERE t.constraint_type = "CHECK"
            AND t.constraint_schema = DATABASE()
            AND t.table_name = %s"""
    cursor = db.execute_sql(sql, (table_name,))
    return [CheckMetadata(name, clause) for name, clause in cursor.fetchall()]


def get_fk_rules(db: Database, table_name: str) -> list[FkRulesMetadata]:
    sql = """
        SELECT kc.table_name, kc.column_name, r.update_rule, r.delete_rule
        FROM information_schema.key_column_usage AS kc
        JOIN information_schema.referential_constraints AS r
            ON kc.constraint_name = r.constraint_name AND kc.constraint_schema = r.constraint_schema
        WHERE (
            kc.constraint_schema = DATABASE()
            AND kc.table_name = %s
        )
    """
    cursor = db.execute_sql(sql, (table_name,))
    return [FkRulesMetadata(*data) for data in cursor.fetchall()]


def get_columns(db: Database, table: str) -> list[ColumnMetadata]:
    """
    Get table columns including column sizes

    There is a very similar function in peewee but it doesn't include the column sizes, whereas this one does
    (data_type vs column_type).
    """
    sql = """
        SELECT column_name, is_nullable, column_type, column_default
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = DATABASE()
        ORDER BY ordinal_position"""
    cursor = db.execute_sql(sql, (table,))
    pks = set(db.get_primary_keys(table))
    return [ColumnMetadata(name, dt, null == "YES", name in pks, table, df) for name, null, dt, df in cursor.fetchall()]


class DbCheckMigrations(ScriptBase):
    """Compare the default database with the schema peewee automatically generates based on the models."""

    subcommand: str = "db-check-migrations"

    @classmethod
    def args(cls, parser: ArgumentParser) -> None:
        parser.description = (
            "Compare the default database with the schema peewee automatically generates based on the models."
        )
        parser.usage = f""" $ cli {cls.subcommand}

        {cls.subcommand} will create a new temporary database schema based on peewee's models, compare with
        the default database and print the differences. The default database can be configured through the
        --environment argument or OBSERVABILITY_CONFIG environment variable.
        """

    @classmethod
    def subcmd_entry_point(cls) -> None:
        init_db()
        with init_temporary_db(TEMP_DB_NAME) as control_db:
            difference = False
            for message in cls.compare_databases(control_db, DB):
                print(message)
                difference = True
            if difference:
                sys.exit(1)
            else:
                print("All checks passed.")

    @classmethod
    def compare_databases(cls, control_db: Database, migrated_db: Database) -> Iterator[str]:
        control_tables = control_db.get_tables()
        for table_name in control_tables:
            yield from cls.compare_tables(control_db, migrated_db, table_name)
        yield from (f"Table {t} should not exist" for t in set(migrated_db.get_tables()) - set(control_tables))

    @classmethod
    def compare_tables(cls, control_db: Database, migrated_db: Database, table_name: str) -> Iterator[str]:
        try:
            migrated_columns = {c.name: c for c in get_columns(migrated_db, table_name)}
        except ProgrammingError as e:
            # Usually happens when the table doesn't exist, but return the original error just in case
            yield str(e)
            return

        for column in get_columns(control_db, table_name):
            try:
                migrated_column = migrated_columns.pop(column.name)
            except KeyError:
                yield f"Column {column} is missing."
                continue
            if migrated_column != column:
                yield f"Column {migrated_column} doesn't match {column}."

        yield from (f"Column {mc} was not expected to exist." for mc in migrated_columns)

        migrated_indexes = {tuple(sorted(i.columns)): i for i in migrated_db.get_indexes(table_name)}
        for index in control_db.get_indexes(table_name):
            try:
                migrated_index = migrated_indexes.pop(tuple(sorted(index.columns)))
            except KeyError:
                yield f"Index {index} is missing."
                continue
            if migrated_index.columns != index.columns or migrated_index.unique != index.unique:
                yield f"Index {migrated_index} doesn't match {index}."

        yield from (f"Index {mi} was not expected to exist." for mi in migrated_indexes.values())

        control_fks = set(control_db.get_foreign_keys(table_name))
        migrated_fks = set(migrated_db.get_foreign_keys(table_name))
        yield from (f"Foreign Key {fk} is missing." for fk in control_fks - migrated_fks)
        yield from (f"Foreign Key {mfk} was not expected to exist." for mfk in migrated_fks - control_fks)

        migrated_checks = {c.name: c for c in get_check_constraints(migrated_db, table_name)}
        for control_check in get_check_constraints(control_db, table_name):
            try:
                migrated_check = migrated_checks.pop(control_check.name)
            except KeyError:
                yield f"Check constraint {control_check.name} is missing."
                continue
            if migrated_check.clause != control_check.clause:
                yield f"Check constraint {migrated_check} doesn't match {control_check}."
        yield from (f"Check constraint {mc.name} was not expected to exist." for mc in migrated_checks.values())

        migrated_rules = {r.column: r for r in get_fk_rules(migrated_db, table_name)}
        for control_rule in get_fk_rules(control_db, table_name):
            try:
                migrated_rule = migrated_rules.pop(control_rule.column)
            except KeyError:
                yield f"FK rules missing for {table_name}.{control_rule.column}."
                continue
            if migrated_rule != control_rule:
                yield f"FK rules {migrated_rule} does not match {control_rule}."
        yield from (f"FK Rules are not expected to exist for {table_name}.{col}." for col in migrated_rules.keys())
