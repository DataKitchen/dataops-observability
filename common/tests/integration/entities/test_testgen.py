from uuid import UUID

import pytest
from peewee import DoesNotExist, IntegrityError

from common.entities import TestgenDatasetComponent


@pytest.fixture
def base_kwargs(dataset):
    return {
        "connection_name": "fake-connection-1",
        "database_name": "fake-database-1",
        "schema": "fake-schema-1",
        "table_list": ["a", "b", "c"],
        "table_include_pattern": ".*?",
        "table_exclude_pattern": ".*?",
        "table_group_id": UUID("72d6eb4f-b2a1-48bd-a36c-332718b8edbd"),
        "project_code": "fake-code-1",
        "uses_sampling": True,
        "sample_percentage": "30%",
        "component": dataset,
        "sample_minimum_count": 3,
    }


@pytest.mark.integration
def test_testgen_dataset_component(base_kwargs):
    inst = TestgenDatasetComponent.create(**base_kwargs)
    assert inst
    inst.save()


@pytest.mark.integration
def test_testgen_dataset_component_default_values(base_kwargs):
    base_kwargs.pop("table_list")
    base_kwargs.pop("uses_sampling")
    inst = TestgenDatasetComponent.create(**base_kwargs)
    assert [] == inst.table_list
    assert inst.uses_sampling is False


@pytest.mark.integration
def test_testgen_dataset_component_uuid_str(base_kwargs):
    base_kwargs["table_group_id"] = "01d51d44-7554-4d0e-aac6-1f4d7e0af3b4"
    inst = TestgenDatasetComponent.create(**base_kwargs)
    assert inst
    inst.save()


@pytest.mark.integration
def test_testgen_dataset_component_on_delete(base_kwargs, dataset):
    inst = TestgenDatasetComponent.create(**base_kwargs)
    total = TestgenDatasetComponent.select().count()
    assert 1 == total, f"Expected 1 TestgenDatasetComponent row, found {total}"

    dataset.delete_instance()
    with pytest.raises(DoesNotExist):
        TestgenDatasetComponent.get_by_id(inst.id)


@pytest.mark.integration
@pytest.mark.parametrize("skip", ("connection_name", "database_name", "component"))
def test_testgen_dataset_component_missing_required(skip, base_kwargs):
    base_kwargs.pop(skip)
    with pytest.raises(IntegrityError):
        TestgenDatasetComponent.create(**base_kwargs)


@pytest.mark.integration
def test_testgen_dataset_component_invalid_table_list(base_kwargs):
    base_kwargs["table_list"] = [1, 2, 3]
    with pytest.raises(ValueError):
        TestgenDatasetComponent.create(**base_kwargs)
