import re
from argparse import ArgumentParser
from typing import Any, Iterable, Optional, Pattern

from peewee import MySQLDatabase

from cli.base import ScriptBase
from common.model import create_all_tables


class MysqlPrintDatabase(MySQLDatabase):
    """Instead of executing the SQL statements, this DB implementation only prints them."""

    _create_table_re: Pattern[str] = re.compile(r"(CREATE TABLE `\w+` \()(.*)(\))")
    _column_split_re: Pattern[str] = re.compile(r",\s*")

    def __init__(self) -> None:
        super().__init__("")

    def execute_sql(self, sql: str, params: Optional[Iterable[Any]] = None, commit: Optional[bool] = None) -> None:
        if params:
            raise Exception(f"Params are not expected to be needed to run DDL SQL, but found {params}")
        if match := self._create_table_re.match(sql):
            sql = "\n".join(
                (
                    match.group(1),
                    ",\n".join([f"  {part}" for part in self._column_split_re.split(match.group(2))]),
                    match.group(3),
                )
            )
        print(sql, end=";\n\n")


class DbSchemaSql(ScriptBase):
    """Outputs the SQL needed to create the database schema."""

    subcommand: str = "db-schema-sql"

    @classmethod
    def args(cls, parser: ArgumentParser) -> None:
        parser.description = "Outputs the SQL needed to create the database schema."
        parser.usage = f"$ cli {cls.subcommand}"

    @staticmethod
    def subcmd_entry_point() -> None:
        print("\n--\n-- SQL statements to create the database schema for Observability\n--\n")
        database = MysqlPrintDatabase()
        create_all_tables(database)
