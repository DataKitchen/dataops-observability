import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

from common.entities import ComponentType, InstanceSet, Project
from common.entities.event import ApiEventType
from testlib.fixtures.entities import *
from testlib.fixtures.v2_events import *


@pytest.fixture
def event_entity(pipeline, run, task, run_task, project, instance, RUNNING_batch_status_event_v2):
    event_entity = RUNNING_batch_status_event_v2.to_event_entity()
    event_entity.project = project
    event_entity.component = pipeline
    event_entity.task = task
    event_entity.run = run
    event_entity.run_task = run_task
    event_entity.instance_set = InstanceSet.get_or_create([instance.id])
    event_entity.save(force_insert=True)
    yield event_entity


@pytest.mark.integration
def test_list_projects(client, g_user, organization, project):
    project_2 = Project.create(name="Bar", organization=organization)
    response = client.get(f"/observability/v1/organizations/{organization.id}/projects")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 2
    assert data["entities"][1]["name"] in (project.name, project_2.name)
    assert data["total"] == 2


@pytest.mark.integration
@pytest.mark.parametrize("auth_method", ["g_user_2", "g_project"], ids=["user from different company", "SA key"])
def test_list_projects_forbidden(client, auth_method, organization, request):
    _ = request.getfixturevalue(auth_method)
    response = client.get(f"/observability/v1/organizations/{organization.id}/projects")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_projects_organization_not_found(client, g_user):
    response = client.get(f"/observability/v1/organizations/{uuid.uuid4()}/projects")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_get_project_by_id(client, g_user, project):
    response = client.get(f"/observability/v1/projects/{project.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(project.id)


@pytest.mark.integration
def test_get_project_by_id_forbidden(client, g_user_2, project, organization):
    response = client.get(f"/observability/v1/projects/{project.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != organization.company.id


@pytest.mark.integration
def test_get_project_by_id_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid.uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


COMMON_EVENT_V1_FIELDS = {
    "pipeline_key",
    "event_timestamp",
    "metadata",
    "run_key",
    "external_url",
    "pipeline_name",
}


@pytest.mark.integration
def test_list_project_events_ok(g_user, client, project, event_entity, instance, journey, pipeline):
    response = client.get(f"/observability/v1/projects/{project.id}/events")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1

    data = response.json["entities"][0]
    assert data["id"] == str(event_entity.id)
    assert data["event_type"] == ApiEventType.BATCH_PIPELINE_STATUS.name
    assert data["project"] == {"id": str(project.id)}
    assert data["run"] == {"id": str(event_entity.run_id)}
    assert data["task"] == {"id": str(event_entity.task.id), "display_name": event_entity.task.name}
    assert data["timestamp"] == event_entity.v2_payload["event_timestamp"]
    assert data["version"] == 2
    assert len(data["components"]) == 1
    assert data["components"][0] == {
        "id": str(event_entity.component_id),
        "display_name": pipeline.display_name,
        "type": ComponentType.BATCH_PIPELINE.value,
        "tool": pipeline.tool,
        "integrations": [],
    }
    assert len(data["instances"]) == 1
    assert data["instances"][0]["journey"] == {"id": str(journey.id)}
    assert data["instances"][0]["instance"] == {"id": str(instance.id)}
    assert data["run_task"] == {"id": str(event_entity.run_task_id)}


@pytest.mark.integration
def test_list_project_events_forbidden(client, g_user_2, project, organization):
    response = client.get(f"/observability/v1/projects/{project.id}/events")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != organization.company.id


@pytest.mark.integration
@pytest.mark.parametrize(
    "range_start, range_end, found",
    (
        (datetime(2023, 1, 1), datetime(2023, 2, 1), 0),
        (datetime(2023, 5, 10), datetime(2023, 5, 12), 1),
        (datetime(2023, 5, 11), datetime(2023, 6, 1), 0),
    ),
)
def test_list_project_events_date_filters(range_start, range_end, found, client, g_user, event_entity, project):
    query_params = f"date_range_start={str(range_start)}&date_range_end={str(range_end)}"

    response = client.get(f"/observability/v1/projects/{project.id}/events?{query_params}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1


@pytest.mark.integration
def test_list_project_events_date_filters(client, g_user, event_entity, project):
    # Invalid date range
    query_params = f"date_range_start={datetime(2022, 1, 2)}&date_range_end={datetime(2021, 1, 1)}"

    response = client.get(f"/observability/v1/projects/{project.id}/events?{query_params}")
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_list_project_events_other_filters(client, g_user, event_entity, project, journey, instance):
    query_params = f"event_type={ApiEventType.BATCH_PIPELINE_STATUS.name}"
    query_params += f"&event_id={event_entity.id}"
    query_params += f"&run_id={event_entity.run_id}"
    query_params += f"&journey_id={journey.id}"
    query_params += f"&component_id={event_entity.component_id}"
    query_params += f"&instance_id={instance.id}"
    query_params += f"&task_id={event_entity.task_id}"

    response = client.get(f"/observability/v1/projects/{project.id}/events?{query_params}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1


@pytest.mark.integration
def test_list_project_events_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid.uuid4()}/events")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
