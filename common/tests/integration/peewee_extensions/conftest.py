import pytest
from peewee import SqliteDatabase

from common.entities import ALL_MODELS, DB


@pytest.fixture
def test_db_base():
    DB.initialize(SqliteDatabase(":memory:", pragmas={"foreign_keys": 1}))
    yield DB
    DB.obj = None


@pytest.fixture
def test_db(test_db_base):
    test_db_base.create_tables(ALL_MODELS)
    yield
    test_db_base.drop_tables(ALL_MODELS)
    test_db_base.close()
