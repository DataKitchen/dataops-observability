import pytest
from peewee import SqliteDatabase

from common.entities import DB, BaseEntity, Company, Pipeline
from common.join_helpers import join_until


@pytest.fixture
def test_db():
    DB.initialize(SqliteDatabase(":memory:", pragmas={"foreign_keys": 1}))
    yield DB
    DB.obj = None


@pytest.fixture
def non_existent_entity_class():
    return type("FakeEntity", (BaseEntity,), {})


@pytest.mark.integration
def test_join_until_missing_path(non_existent_entity_class):
    with pytest.raises(ValueError, match="No known path to join"):
        join_until(Pipeline.select(), non_existent_entity_class)


@pytest.mark.integration
def test_join_until(test_db):
    query = join_until(Pipeline.select(), Company)
    assert str(query).count("JOIN") == 4
