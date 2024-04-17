import uuid
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from uuid import uuid4

import pytest
from werkzeug.datastructures import MultiDict

from common.datetime_utils import datetime_iso8601, timestamp_to_datetime
from common.entities import AlertLevel, Instance, InstanceAlert, InstanceAlertType, RunAlertType


@pytest.mark.integration
def test_list_project_alerts(client, g_user, project, instance_alert, instance_alert_components, run_alert):
    response = client.get(f"/observability/v1/projects/{project.id}/alerts")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["total"] == 2
    actual_run_alert = data["entities"][0]
    assert actual_run_alert == {
        "created_on": datetime_iso8601(run_alert.created_on),
        "description": run_alert.description,
        "details": {
            "expected_start_time": timestamp_to_datetime(run_alert.details["expected_start_time"]).isoformat(),
            "expected_end_time": timestamp_to_datetime(run_alert.details["expected_end_time"]).isoformat(),
        },
        "level": run_alert.level.value,
        "type": run_alert.type.value,
        "run": {"id": str(run_alert.run.id), "key": run_alert.run.key, "name": run_alert.run.name},
        "instance": None,
        "components": None,
    }
    actual_instance_alert = data["entities"][1]
    assert actual_instance_alert["created_on"] == datetime_iso8601(instance_alert.created_on)
    assert actual_instance_alert["description"] == instance_alert.description
    assert (
        actual_instance_alert["details"]["expected_start_time"]
        == timestamp_to_datetime(instance_alert.details["expected_start_time"]).isoformat()
    )
    assert (
        actual_instance_alert["details"]["expected_end_time"]
        == timestamp_to_datetime(instance_alert.details["expected_end_time"]).isoformat()
    )
    assert actual_instance_alert["level"] == instance_alert.level.value
    assert actual_instance_alert["type"] == instance_alert.type.value
    assert actual_instance_alert["instance"] == str(instance_alert.instance.id)
    assert sorted(actual_instance_alert["components"], key=lambda x: x["display_name"]) == sorted(
        [
            {
                "id": str(iac.component.id),
                "display_name": iac.component.display_name,
                "type": iac.component.type,
                "tool": iac.component.tool,
            }
            for iac in instance_alert_components
        ],
        key=lambda x: x["display_name"],
    )
    assert actual_run_alert["created_on"] > actual_instance_alert["created_on"]


@pytest.mark.integration
def test_list_project_alerts_pagination(client, g_user, project, instance_alert, instance_alert_components, run_alerts):
    # Default: page 1, count 10, and sorted by created on field
    response = client.get(f"/observability/v1/projects/{project.id}/alerts")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 13
    assert len(response.json["entities"]) == 10
    assert response.json["entities"][0]["description"] == "Description of run alert 5"

    response = client.get(f"/observability/v1/projects/{project.id}/alerts?count=1&page=2")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 13
    assert len(response.json["entities"]) == 1
    assert response.json["entities"][0]["description"] == "Description of run alert 4"


@pytest.mark.integration
def test_list_project_alerts_sort(client, g_user, project, instance_alert, instance_alert_components, run_alerts):
    # Default: sorted by created_on desc
    response = client.get(f"/observability/v1/projects/{project.id}/alerts")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["entities"][0]["description"] == "Description of run alert 5"

    instance_alert.update({"created_on": datetime.now() - timedelta(days=1)}).execute()
    response = client.get(f"/observability/v1/projects/{project.id}/alerts?count=100&sort=asc")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["entities"][0]["description"] == instance_alert.description


@pytest.mark.integration
def test_list_project_alerts_search(client, g_user, project, instance_alert, instance_alert_components, run_alerts):
    # lower case
    response = client.get(f"/observability/v1/projects/{project.id}/alerts?search=instance")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    assert len(response.json["entities"]) == 1
    assert response.json["entities"][0]["description"] == instance_alert.description

    # upper case
    response = client.get(f"/observability/v1/projects/{project.id}/alerts?search=INSTANCE")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    assert len(response.json["entities"]) == 1
    assert response.json["entities"][0]["description"] == instance_alert.description


@pytest.mark.integration
def test_list_project_alerts_filters(client, g_user, project, instance_alert, instance_alert_components, run_alerts):
    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
    past_instance = Instance.create(journey=instance_alert.instance.journey, start_time=yesterday)
    past_instance_alert = InstanceAlert.create(
        id=uuid4(),
        instance=past_instance,
        name="past-instance-alert",
        description="past instance alert ",
        message="past instance alert was generated",
        level=AlertLevel.ERROR,
        type=InstanceAlertType.INCOMPLETE,
        created_on=yesterday,
    )

    # Base case: no filters
    response = client.get(f"/observability/v1/projects/{project.id}/alerts")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 14

    query_string = MultiDict([("instance_id", past_instance.id)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    assert response.json["entities"][0]["description"] == past_instance_alert.description

    start_time = instance_alert.instance.start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    query_string = MultiDict([("date_range_start", start_time)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    # not include past_instance_alert
    assert response.json["total"] == 13

    query_string = MultiDict([("date_range_end", yesterday + timedelta(minutes=1))])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1

    query_string = MultiDict([("level", AlertLevel.ERROR.value)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    # include all alerts, except instance_alert, which has WARNING level
    assert response.json["total"] == 13
    assert all(r["level"] == AlertLevel.ERROR.value for r in response.json["entities"])

    query_string = MultiDict([("type", InstanceAlertType.INCOMPLETE.value), ("type", RunAlertType.LATE_START.value)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 7
    assert all(r["type"] == RunAlertType.LATE_START.value for r in response.json["entities"][:6])
    assert response.json["entities"][-1]["type"] == past_instance_alert.type.value

    # test component filter for instance alerts
    query_string = MultiDict([("component_id", instance_alert_components[1].component.id)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1
    assert len(response.json["entities"][0]["components"]) == 2
    assert any(
        c["id"] == str(instance_alert_components[1].component.id) for c in response.json["entities"][0]["components"]
    )

    # test component filter for run alerts
    comp_id = run_alerts[0].run.pipeline.id
    query_string = MultiDict([("component_id", comp_id)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 13
    expected_runs = {str(r.run.id) for r in run_alerts if r.run.pipeline.id == comp_id}
    assert {r["run"]["id"] for r in response.json["entities"]} == expected_runs

    # test component filter true negative case
    query_string = MultiDict([("component_id", uuid4())])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0

    query_string = MultiDict([("run_id", run_alerts[0].run.id)])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 2
    assert all(r["run"]["id"] == str(run_alerts[0].run.id) for r in response.json["entities"])

    query_string = MultiDict([("run_key", "1"), ("run_key", "2")])
    response = client.get(f"/observability/v1/projects/{project.id}/alerts", query_string=query_string)
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 4
    assert all(r["run"]["key"] in ["1", "2"] for r in response.json["entities"])


@pytest.mark.integration
def test_get_project_alerts_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid.uuid4()}/alerts")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_project_alerts_forbidden(
    client, g_user_2, project, instance_alert, instance_alert_components, run_alerts
):
    response = client.get(f"/observability/v1/projects/{project.id}/alerts")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != project.organization.company.id
