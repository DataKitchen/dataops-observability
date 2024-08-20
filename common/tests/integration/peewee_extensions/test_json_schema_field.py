from datetime import date

import pytest
from marshmallow import Schema
from marshmallow.fields import Date
from peewee import IntegrityError, SQL

from common.entities.base_entity import BaseEntity
from common.peewee_extensions.fields import JSONSchemaField


class CoolSchema(Schema):
    nested_field = Date()


class FakeTestModel(BaseEntity):
    object_field = JSONSchemaField(CoolSchema())
    object_field_nullable = JSONSchemaField(CoolSchema(), null=True)
    object_field_default = JSONSchemaField(CoolSchema(), default={"nested_field": date(2011, 3, 13)})
    list_field = JSONSchemaField(CoolSchema(many=True))
    list_field_nullable = JSONSchemaField(CoolSchema(many=True), null=True)
    list_field_default = JSONSchemaField(CoolSchema(many=True), default=[{"nested_field": date(2011, 3, 13)}])


@pytest.fixture
def test_data():
    return {"nested_field": date(2024, 7, 1)}


@pytest.fixture
def default_data():
    return {"nested_field": date(2011, 3, 13)}


@pytest.fixture
def bad_data():
    return {"nested_field": 1}


@pytest.fixture
def temp_db(test_db_base):
    test_db_base.create_tables([FakeTestModel])
    yield
    test_db_base.drop_tables([FakeTestModel])
    test_db_base.close()


@pytest.mark.integration
def test_save_and_get(temp_db, test_data):
    FakeTestModel.create(
        object_field=test_data,
        object_field_nullable=test_data,
        object_field_default=test_data,
        list_field=[test_data, test_data],
        list_field_nullable=[test_data, test_data],
        list_field_default=[test_data, test_data],
    )

    retrieved = FakeTestModel.select().get()

    assert retrieved.object_field == test_data, retrieved.object_field
    assert retrieved.object_field_nullable == test_data, retrieved.object_field_nullable
    assert retrieved.object_field_default == test_data, retrieved.object_field_default
    assert retrieved.list_field == [test_data, test_data], retrieved.list_field
    assert retrieved.list_field_nullable == [test_data, test_data], retrieved.list_field_nullable
    assert retrieved.list_field_default == [test_data, test_data], retrieved.list_field_default


@pytest.mark.integration
def test_save_and_get_default(temp_db, test_data, default_data):
    FakeTestModel.create(
        object_field=test_data,
        list_field=[test_data, test_data],
    )

    retrieved = FakeTestModel.select().get()

    assert retrieved.object_field == test_data, retrieved.object_field
    assert retrieved.object_field_nullable == None, retrieved.object_field_nullable
    assert retrieved.object_field_default == default_data, retrieved.object_field_default
    assert retrieved.list_field == [test_data, test_data], retrieved.list_field
    assert retrieved.list_field_nullable == None, retrieved.list_field_nullable
    assert retrieved.list_field_default == [default_data], retrieved.list_field_default


@pytest.mark.integration
def test_save_integrity_error(temp_db):
    with pytest.raises(IntegrityError):
        FakeTestModel.create()


@pytest.mark.integration
def test_dump_error(temp_db, test_data, bad_data):
    with pytest.raises(ValueError, match=".*object_field.*dumped"):
        FakeTestModel.create(
            object_field=bad_data,
            list_field=[test_data],
        )


@pytest.mark.integration
def test_load_error(temp_db, test_data, bad_data):
    entity = FakeTestModel.create(
        object_field=test_data,
        list_field=[test_data],
    )
    entity.update(object_field=SQL("JSON_ARRAY('[1,2,3]')")).execute()

    with pytest.raises(ValueError, match=".*object_field.*loaded"):
        FakeTestModel.select().get()
