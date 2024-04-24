import pytest
from peewee import SqliteDatabase

from common.entities import DB


@pytest.fixture
def test_db():
    DB.initialize(SqliteDatabase(":memory:", pragmas={"foreign_keys": 1}))
    yield DB
    DB.obj = None
