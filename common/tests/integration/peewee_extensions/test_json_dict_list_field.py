import pytest

from common.entities.base_entity import BaseEntity
from common.peewee_extensions.fields import JSONDictListField


class FakeTestModel(BaseEntity):
    cool_list = JSONDictListField()


@pytest.fixture
def temp_db(test_db_base):
    test_db_base.create_tables([FakeTestModel])
    yield
    test_db_base.drop_tables([FakeTestModel])
    test_db_base.close()


@pytest.mark.integration
def test_json_dict_list_field_save_load(temp_db):
    """The JSONDictListField can save and retrieve lists of mapping data."""
    important_data = [{"a": 1, "b": 2}, {"a": 5, "b": 99}]

    FakeTestModel.create(cool_list=important_data)
    retrieved = FakeTestModel.select().get()

    assert important_data == retrieved.cool_list
