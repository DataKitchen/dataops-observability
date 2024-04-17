import pytest

from common.entities.base_entity import BaseEntity
from common.peewee_extensions.fields import JSONStrListField


class FakeTestModel(BaseEntity):
    cool_list = JSONStrListField()


@pytest.fixture
def temp_db(test_db_base):
    test_db_base.create_tables([FakeTestModel])
    yield
    test_db_base.drop_tables([FakeTestModel])
    test_db_base.close()


@pytest.mark.integration
def test_json_str_list_field_save_load(temp_db):
    """The JSONStrListField can save and retrieve lists of string data."""
    important_data = ["a", "b", "c"]

    FakeTestModel.create(cool_list=important_data)
    retrieved = FakeTestModel.select().get()

    assert important_data == retrieved.cool_list
