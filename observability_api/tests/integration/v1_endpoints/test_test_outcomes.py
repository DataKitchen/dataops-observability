from datetime import datetime, timedelta
from http import HTTPStatus
from uuid import UUID, uuid4

import pytest

from common.entities import TestGenTestOutcomeIntegration
from common.events.v1 import TestStatuses
from observability_api.schemas.testgen_test_outcome_schemas import Integration
from observability_api.tests.integration.v1_endpoints.conftest import TIMESTAMP_FORMAT


@pytest.mark.integration
def test_tests_not_found(client, g_user, instance):
    response = client.get(f"/observability/v1/projects/{uuid4()}/tests")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_tests_forbidden(client, g_user_2, project):
    response = client.get(f"/observability/v1/projects/{project.id}/tests")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_test_outcomes(client, g_user, project, test_outcome, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    data = response.json["entities"][0]
    assert data["name"] == test_outcome.name
    assert data["status"] == test_outcome.status
    assert data["description"] == test_outcome.description
    assert datetime.strptime(data["start_time"], TIMESTAMP_FORMAT) == test_outcome.start_time
    assert datetime.strptime(data["end_time"], TIMESTAMP_FORMAT) == test_outcome.end_time
    assert data["metric_value"] == str(test_outcome.metric_value)
    assert data["min_threshold"] == str(test_outcome.min_threshold)
    assert data["max_threshold"] == str(test_outcome.max_threshold)
    assert data["component"]["id"] == str(pipeline.id)
    assert data["component"]["tool"] == pipeline.tool
    assert data["external_url"] == test_outcome.external_url
    assert data["result"] == test_outcome.result
    assert data["type"] == test_outcome.type
    assert data["key"] == test_outcome.key
    assert data["dimensions"] == test_outcome.dimensions
    assert data["metric_name"] == test_outcome.metric_name
    assert data["metric_description"] == test_outcome.metric_description


@pytest.mark.integration
def test_test_outcomes_list_integrations(client, g_user, project, test_outcome, pipeline):
    ti_1 = TestGenTestOutcomeIntegration.create(
        id=UUID("4820da79-6807-4409-9ec2-06c9ae09a88b"),
        test_outcome=test_outcome,
        columns=["a", "b"],
        test_parameters=[{"name": "retry"}, {"value": 2.0}],
        version=1,
        test_suite="test-suite-1",
        table="table-1",
    )
    response = client.get(f"/observability/v1/projects/{project.id}/tests")
    assert response.json["total"] == 1
    data = response.json["entities"][0]
    assert data["id"] == str(test_outcome.id)
    assert len(data["integrations"]) == 1
    assert data["integrations"][0] == {
        "id": str(ti_1.id),
        "table": ti_1.table,
        "columns": ti_1.columns,
        "test_suite": ti_1.test_suite,
        "version": ti_1.version,
        "test_outcome": str(test_outcome.id),
        "test_parameters": [{"name": "retry"}, {"value": "2.0"}],
        "integration_name": Integration.TESTGEN.name,
    }


@pytest.mark.integration
def test_test_outcomes_instance_filter(client, g_user, project, instance, test_outcome, pipeline):
    response = client.get(
        f"/observability/v1/projects/{project.id}/tests", query_string={"instance_id": str(instance.id)}
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    data = response.json["entities"][0]
    assert data["name"] == test_outcome.name
    assert data["status"] == test_outcome.status


@pytest.mark.integration
def test_test_outcomes_instance_filter_no_results(client, g_user, project, test_outcome, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"instance_id": str(uuid4())})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0


@pytest.mark.integration
def test_test_outcomes_key_filter(client, g_user, project, instance, test_outcome, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"key": test_outcome.key})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    data = response.json["entities"][0]
    assert data["name"] == test_outcome.name
    assert data["status"] == test_outcome.status


@pytest.mark.integration
def test_test_outcomes_key_filter_no_results(client, g_user, project, test_outcome, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"key": "unknown-key"})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0


@pytest.mark.integration
def test_test_outcomes_run_filter(client, g_user, project, run, test_outcome, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"run_id": str(run.id)})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    data = response.json["entities"][0]
    assert data["name"] == test_outcome.name
    assert data["status"] == test_outcome.status


@pytest.mark.integration
def test_test_outcomes_run_filter_no_results(client, g_user, project, run, test_outcome, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"run_id": str(uuid4())})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0


@pytest.mark.integration
def test_test_outcomes_filter_combine_instance_and_run_filter(
    client, g_user, project, run, instance, test_outcome, pipeline
):
    response = client.get(
        f"/observability/v1/projects/{project.id}/tests",
        query_string={"run_id": str(run.id), "instance_id": str(instance.id)},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    data = response.json["entities"][0]
    assert data["name"] == test_outcome.name
    assert data["status"] == test_outcome.status


@pytest.mark.integration
def test_test_outcomes_sort(client, g_user, project, test_outcomes, pipeline):
    # Default sort: ASC (by start_time)
    response = client.get(f"/observability/v1/projects/{project.id}/tests")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 2
    assert len(response.json["entities"]) == 2
    data = response.json["entities"]
    assert data[0]["start_time"] < data[1]["start_time"]
    for idx, test_outcome in enumerate(test_outcomes):
        assert data[idx]["name"] == test_outcome.name
        assert data[idx]["status"] == test_outcome.status
        assert data[idx]["description"] == test_outcome.description

    # DESC sort
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"sort": "desc"})
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 2
    data = response.json["entities"]
    assert data[0]["start_time"] > data[1]["start_time"]


@pytest.mark.integration
def test_test_outcomes_pagination(client, g_user, project, test_outcomes, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/tests", query_string={"page": 2, "count": 1})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 2
    assert len(response.json["entities"]) == 1
    data = response.json["entities"][0]
    assert data["name"] == test_outcomes[1].name
    assert data["status"] == test_outcomes[1].status
    assert data["description"] == test_outcomes[1].description


@pytest.mark.integration
def test_test_outcome_invalid_filter(client, g_user, project, test_outcome):
    start = datetime.now() - timedelta(days=1)
    end = datetime.now() + timedelta(days=1)
    query_param = f"start_range_begin={end}&start_range_end={start}"
    response = client.get(f"/observability/v1/projects/{project.id}/tests?{query_param}")
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
@pytest.mark.parametrize(
    "query_string,expected_total",
    (
        ("search=abc", 1),
        ("search=description", 1),
        ("search=nan", 0),
        (f"status={TestStatuses.WARNING.name}&component_id=PIPELINE_ID", 1),
        (f"status={TestStatuses.FAILED.name}&status={TestStatuses.PASSED.name}", 0),
        ("start_range_begin=START&start_range_end=END", 1),
        ("end_range_begin=START&end_range_end=END", 1),
        ("start_range_begin=END", 0),
        ("start_range_end=START", 0),
        ("end_range_begin=END", 0),
        ("end_range_end=START", 0),
    ),
)
def test_test_outcome_filters(client, g_user, project, pipeline, test_outcome, query_string, expected_total):
    query_string = query_string.replace("PIPELINE_ID", str(pipeline.id))
    query_string = query_string.replace("START", str(datetime.now() - timedelta(days=1)))
    query_string = query_string.replace("END", str(datetime.now() + timedelta(days=1)))
    response = client.get(f"/observability/v1/projects/{project.id}/tests?{query_string}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == expected_total


@pytest.mark.integration
def test_get_test_outcome_by_id(client, test_outcome, g_user):
    response = client.get(f"/observability/v1/test-outcomes/{test_outcome.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(test_outcome.id)


@pytest.mark.integration
def test_get_test_outcome_by_id_not_found(client, test_outcome, g_user):
    response = client.get("/observability/v1/test-outcomes/bcad89d9-c721-443e-baa6-0462db1fa2bf")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
