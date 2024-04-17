import pytest

from observability_api.schemas import TestgenDatasetComponentSchema


@pytest.mark.integration
def test_testgen_dataset_component_dump(testgen_dataset_component):
    expected = {
        "component": str(testgen_dataset_component.component_id),
        "connection_name": "dataset-component-connection-d4b66e29",
        "database_name": "dataset-component-db-d4b66e29",
        "id": str(testgen_dataset_component.id),
        "project_code": "dataset-project-code-d4b66e29",
        "sample_minimum_count": None,
        "sample_percentage": None,
        "schema": "dataset-component-schema-d4b66e29",
        "table_exclude_pattern": None,
        "table_group_id": "c28c9306-fa91-4a3f-8f29-36d56c447c81",
        "table_include_pattern": None,
        "table_list": ["a", "b", "c"],
        "uses_sampling": False,
        "integration_name": "TESTGEN",
    }
    actual = TestgenDatasetComponentSchema().dump(testgen_dataset_component)
    assert expected == actual
