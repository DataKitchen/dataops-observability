from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import pytest
from werkzeug.datastructures import MultiDict

from common.entities import InstanceRule, InstanceRuleAction, Journey, Project
from testlib.fixtures.entities import *


@pytest.mark.integration
def test_list_project_upcoming_instances_instance_schedule(client, journey, journey_2, instance, g_user):
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, expression="1,20 * * * *")
    InstanceRule.create(journey=journey, action=InstanceRuleAction.END, expression="30,40 * * * *")
    InstanceRule.create(journey=journey_2, action=InstanceRuleAction.START, expression="10,50 * * * *")

    start_time = datetime(1991, 2, 20, 10, 00, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("end_range", (start_time + timedelta(hours=1)).isoformat()),
        ]
    )
    response = client.get(f"/observability/v1/projects/{journey.project.id}/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json

    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 5
    assert upcoming_instances[0]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[0]["project"]["name"] == journey.project.name
    assert upcoming_instances[0]["journey"]["id"] == str(journey.id)
    assert datetime.fromisoformat(upcoming_instances[0]["expected_start_time"]) == start_time + timedelta(minutes=1)
    assert upcoming_instances[0]["expected_end_time"] is None

    assert upcoming_instances[1]["project"]["id"] == str(journey_2.project.id)
    assert upcoming_instances[1]["journey"]["id"] == str(journey_2.id)
    assert datetime.fromisoformat(upcoming_instances[1]["expected_start_time"]) == start_time + timedelta(minutes=10)
    assert upcoming_instances[1]["expected_end_time"] is None

    assert upcoming_instances[2]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[2]["journey"]["id"] == str(journey.id)
    assert datetime.fromisoformat(upcoming_instances[2]["expected_start_time"]) == start_time + timedelta(minutes=20)
    assert datetime.fromisoformat(upcoming_instances[2]["expected_end_time"]) == start_time + timedelta(minutes=30)

    assert upcoming_instances[3]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[3]["journey"]["id"] == str(journey.id)
    assert upcoming_instances[3]["expected_start_time"] is None
    assert datetime.fromisoformat(upcoming_instances[3]["expected_end_time"]) == start_time + timedelta(minutes=40)

    assert upcoming_instances[4]["project"]["id"] == str(journey_2.project.id)
    assert upcoming_instances[4]["journey"]["id"] == str(journey_2.id)
    assert datetime.fromisoformat(upcoming_instances[4]["expected_start_time"]) == start_time + timedelta(minutes=50)
    assert upcoming_instances[4]["expected_end_time"] is None


@pytest.mark.integration
def test_list_project_upcoming_instances_batch_schedule(
    client,
    journey,
    instance,
    pipeline,
    batch_start_schedule,
    batch_end_schedule,
    instance_rule_pipeline_start,
    instance_rule_pipeline_end,
    g_user,
):
    batch_start_schedule.schedule = "0 * * * *"
    batch_start_schedule.save()
    batch_end_schedule.schedule = "30 * * * *"
    batch_end_schedule.save()

    start_time = datetime(1991, 2, 20, 10, 59, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("count", 25),
        ]
    )
    response = client.get(f"/observability/v1/projects/{journey.project.id}/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json

    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 25
    for i, upcoming in enumerate(upcoming_instances):
        assert upcoming["project"]["id"] == str(journey.project.id)
        assert upcoming["journey"]["id"] == str(journey.id)
        assert datetime.fromisoformat(upcoming["expected_start_time"]) == start_time + timedelta(minutes=i * 60 + 1)
        assert datetime.fromisoformat(upcoming["expected_end_time"]) == start_time + timedelta(minutes=i * 60 + 31)


@pytest.mark.integration
def test_list_project_upcoming_instances_filters(client, journey, journey_2, instance, g_user):
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, expression="10 * * * *")
    InstanceRule.create(journey=journey_2, action=InstanceRuleAction.START, expression="30 * * * *")

    start_time = datetime(1991, 2, 20, 10, 00, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("count", 2),
        ]
    )
    response = client.get(f"/observability/v1/projects/{journey.project.id}/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json
    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 2
    assert upcoming_instances[0]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[0]["journey"]["id"] == str(journey.id)
    assert upcoming_instances[1]["project"]["id"] == str(journey_2.project.id)
    assert upcoming_instances[1]["journey"]["id"] == str(journey_2.id)

    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("count", 2),
            ("journey_id", str(journey.id)),
        ]
    )
    response = client.get(f"/observability/v1/projects/{journey.project.id}/upcoming-instances", query_string=query)
    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 2
    assert upcoming_instances[0]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[0]["journey"]["id"] == str(journey.id)
    assert upcoming_instances[1]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[1]["journey"]["id"] == str(journey.id)

    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("count", 2),
            ("journey_name", journey_2.name),
        ]
    )
    response = client.get(f"/observability/v1/projects/{journey.project.id}/upcoming-instances", query_string=query)
    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 2
    assert upcoming_instances[0]["project"]["id"] == str(journey_2.project.id)
    assert upcoming_instances[0]["journey"]["id"] == str(journey_2.id)
    assert upcoming_instances[1]["project"]["id"] == str(journey_2.project.id)
    assert upcoming_instances[1]["journey"]["id"] == str(journey_2.id)


@pytest.mark.integration
def test_list_company_upcoming_instances_instance_schedule(client, organization, journey, instance, g_user):
    project_2 = Project.create(name="test project 2", organization=organization, active=True)
    journey_2 = Journey.create(name="test journey 2", project=project_2)
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, expression="10 * * * *")
    InstanceRule.create(journey=journey_2, action=InstanceRuleAction.START, expression="30 * * * *")

    start_time = datetime(1991, 2, 20, 10, 00, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
        ]
    )
    response = client.get("/observability/v1/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json

    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 10
    for i, upcoming in enumerate(upcoming_instances):
        assert upcoming["project"]["id"] == str(journey.project.id) if i % 2 == 0 else str(journey_2.project.id)
        assert upcoming["journey"]["id"] == str(journey.id) if i % 2 == 0 else str(journey_2.id)
        assert upcoming["expected_start_time"] is not None
        assert upcoming["expected_end_time"] is None


@pytest.mark.integration
def test_list_company_upcoming_instances_filters(client, project, organization, journey, instance, g_user):
    project_2 = Project.create(name="test project 2", organization=organization, active=True)
    journey_2 = Journey.create(name="test journey 2", project=project_2)
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, expression="10 * * * *")
    InstanceRule.create(journey=journey_2, action=InstanceRuleAction.START, expression="30 * * * *")

    start_time = datetime(1991, 2, 20, 10, 00, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("count", 2),
        ]
    )
    response = client.get("/observability/v1/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json

    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 2
    assert upcoming_instances[0]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[0]["journey"]["id"] == str(journey.id)
    assert upcoming_instances[1]["project"]["id"] == str(journey_2.project.id)
    assert upcoming_instances[1]["journey"]["id"] == str(journey_2.id)

    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("count", 2),
            ("project_id", str(project.id)),
        ]
    )
    response = client.get("/observability/v1/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json

    upcoming_instances = response.json["entities"]
    assert len(upcoming_instances) == 2
    assert upcoming_instances[0]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[0]["journey"]["id"] == str(journey.id)
    assert upcoming_instances[1]["project"]["id"] == str(journey.project.id)
    assert upcoming_instances[1]["journey"]["id"] == str(journey.id)


@pytest.mark.integration
def test_list_project_upcoming_instances_sa_key_auth_ok(client, journey, journey_2, instance, g_project):
    start_time = datetime(1991, 2, 20, 10, 00, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("end_range", (start_time + timedelta(hours=1)).isoformat()),
        ]
    )
    response = client.get(f"/observability/v1/projects/{journey.project.id}/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
def test_list_company_upcoming_instances_sa_key_auth_forbidden(client, journey, journey_2, instance, g_project):
    start_time = datetime(1991, 2, 20, 10, 00, 00, tzinfo=timezone.utc)
    query = MultiDict(
        [
            ("start_range", start_time.isoformat()),
            ("end_range", (start_time + timedelta(hours=1)).isoformat()),
        ]
    )
    response = client.get("/observability/v1/upcoming-instances", query_string=query)
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
