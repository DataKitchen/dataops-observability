from http import HTTPStatus
from uuid import uuid4

import pytest

from common.entities import Schedule, ScheduleExpectation
from observability_api.endpoints.v1.schedules import EXPECTATION_TO_COMPONENT


@pytest.fixture
def schedule_data():
    return {
        "timezone": "America/Sao_Paulo",
        "expectation": ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
        "schedule": "* 10 1-2 * *",
        "margin": 900,
        "description": "A cool Schedule",
    }


@pytest.fixture
def schedule(pipeline, schedule_data):
    yield Schedule.create(component=pipeline, **schedule_data)


@pytest.mark.integration
def test_list_schedules(client, pipeline, schedule_data, g_user):
    schedule_data.pop("expectation")
    schedule_data.pop("schedule")
    schedule1 = Schedule.create(
        component=pipeline,
        schedule="0 20 * * *",
        expectation=ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
        **schedule_data,
    )
    schedule2 = Schedule.create(
        component=pipeline,
        schedule="0 22 * * *",
        expectation=ScheduleExpectation.BATCH_PIPELINE_END_TIME.value,
        **schedule_data,
    )

    response = client.get(f"/observability/v1/components/{pipeline.id}/schedules")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["entities"]) == 2
    assert data["entities"][0]["schedule"] == schedule1.schedule
    assert data["entities"][1]["schedule"] == schedule2.schedule


@pytest.mark.integration
def test_list_schedules_not_member(client, schedule, g_user_2):
    response = client.get(f"/observability/v1/components/{schedule.component.id}/schedules")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert "entities" not in response.json, response.json


@pytest.mark.integration
def test_list_schedules_admin(client, schedule, g_user_2_admin):
    response = client.get(f"/observability/v1/components/{schedule.component.id}/schedules")
    assert response.status_code == HTTPStatus.OK, response.json
    assert "entities" in response.json, response.json


@pytest.mark.integration
def test_list_schedules_pipeline_not_found(client, g_user):
    response = client.get(f"/observability/v1/components/{uuid4()}/schedules")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_schedule_ok(client, pipeline, schedule_data, g_user):
    response = client.post(
        f"/observability/v1/components/{pipeline.id}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert Schedule.select().count() == 1
    resp_data = response.json
    assert resp_data["id"] is not None
    assert resp_data["timezone"] == schedule_data["timezone"]
    assert resp_data["expectation"] == schedule_data["expectation"]
    assert resp_data["schedule"] == schedule_data["schedule"]
    assert resp_data["margin"] == schedule_data["margin"]
    assert resp_data["description"] == schedule_data["description"]
    assert resp_data["component"] == str(pipeline.id)
    assert resp_data["created_by"]["id"] == str(g_user.id)
    assert resp_data["created_on"] is not None


@pytest.mark.integration
def test_post_schedule_conflict(client, pipeline, schedule, schedule_data, g_user):
    response = client.post(
        f"/observability/v1/components/{pipeline.id}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json
    assert Schedule.select().count() == 1


@pytest.mark.integration
def test_post_schedule_not_member(client, pipeline, schedule_data, g_user_2):
    response = client.post(
        f"/observability/v1/components/{pipeline.id}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert Schedule.select().count() == 0


@pytest.mark.integration
def test_post_schedule_admin(client, pipeline, schedule_data, g_user_2_admin):
    response = client.post(
        f"/observability/v1/components/{pipeline.id}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert Schedule.select().count() == 1


@pytest.mark.integration
def test_post_schedule_pipeline_not_found(client, schedule_data, g_user):
    response = client.post(
        f"/observability/v1/components/{uuid4()}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_schedule_invalid_field(client, pipeline, g_user):
    response = client.post(
        f"/observability/v1/components/{pipeline.id}/schedules",
        headers={"Content-Type": "application/json"},
        json={"invalid_field": "a data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
@pytest.mark.parametrize(
    "expectation, margin, valid_component_fixture, invalid_component_fixture",
    (
        (ScheduleExpectation.BATCH_PIPELINE_START_TIME, 60, "pipeline", "server"),
        (ScheduleExpectation.BATCH_PIPELINE_END_TIME, None, "pipeline", "dataset"),
        (ScheduleExpectation.DATASET_ARRIVAL, 60, "dataset", "stream"),
    ),
)
def test_post_schedule_type_mapping(
    request, client, expectation, valid_component_fixture, invalid_component_fixture, margin, g_user, schedule_data
):
    valid_component = request.getfixturevalue(valid_component_fixture)
    invalid_component = request.getfixturevalue(invalid_component_fixture)
    schedule_data["expectation"] = expectation.name
    schedule_data["margin"] = margin

    response = client.post(
        f"/observability/v1/components/{valid_component.id}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json

    response = client.post(
        f"/observability/v1/components/{invalid_component.id}/schedules",
        headers={"Content-Type": "application/json"},
        json=schedule_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_expectation_to_component_map():
    """Test that all expectations are listed in EXPECTATION_TO_COMPONENT"""
    for expectation in ScheduleExpectation:
        assert expectation.value in EXPECTATION_TO_COMPONENT


@pytest.mark.integration
def test_delete_schedule_ok(client, schedule, g_user):
    assert Schedule.select().count() == 1
    response = client.delete(f"/observability/v1/schedules/{schedule.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert Schedule.select().count() == 0


@pytest.mark.integration
def test_delete_schedule_not_member(client, schedule, g_user_2):
    assert Schedule.select().count() == 1
    response = client.delete(f"/observability/v1/schedules/{schedule.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert Schedule.select().count() == 1


@pytest.mark.integration
def test_delete_schedule_admin(client, schedule, g_user_2_admin):
    assert Schedule.select().count() == 1
    response = client.delete(f"/observability/v1/schedules/{schedule.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert Schedule.select().count() == 0


@pytest.mark.integration
def test_delete_schedule_not_found(client, schedule, g_user):
    assert Schedule.select().count() == 1
    response = client.delete(f"/observability/v1/schedules/{uuid4()}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert Schedule.select().count() == 1
