import pytest

from observability_api.schemas import InstanceDagSchema, InstanceDagNodeSchema
from testlib.fixtures.entities import *


@pytest.mark.unit
def test_instance_dag_schema_dump():
    data = InstanceDagSchema().dump({"nodes": []})

    assert isinstance(data["nodes"], list)


@pytest.mark.unit
def test_instance_dag_node_schema_dump(component, pipeline):
    edges = [
        {"id": "1", "left": None},
        {"id": "2", "left": pipeline},
    ]

    data = InstanceDagNodeSchema().dump(
        {
            "component": component,
            "status": "RUNNING",
            "edges": edges,
            "runs_summary": [
                {"status": "COMPLETED_WITH_WARNINGS", "count": 1},
                {"status": "PENDING", "count": 2},
            ],
            "alerts_summary": [
                {"level": "WARNING", "description": "...", "count": 1},
            ],
            "tests_summary": [
                {"status": "PASSED", "count": 3},
                {"status": "FAILED", "count": 3},
            ],
            "operations_summary": [
                {"operation": "WRITE", "count": 2},
            ],
        }
    )

    assert data["component"]["id"] == str(component.id)
    assert data["status"] == "RUNNING"
    assert data["edges"][1]["component"] == str(pipeline.id)
    assert [summary for summary in data["runs_summary"] if summary["status"] == "PENDING"][0]["count"] == 2
