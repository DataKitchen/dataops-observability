import uuid
from http import HTTPStatus

import pytest

from common.entities import InstanceRule, InstanceRuleAction


@pytest.fixture
def instance_rule_schedule_data():
    return {"expression": "* 10 1-2 * *", "timezone": "America/New_York"}


@pytest.fixture
def instance_rule(journey, pipeline):
    return InstanceRule.create(journey=journey, action=InstanceRuleAction.START, batch_pipeline=pipeline)


@pytest.mark.integration
def test_delete_instance_rule(client, g_user, instance_rule):
    assert InstanceRule.select().count() == 1
    response = client.delete(f"/observability/v1/instance-conditions/{instance_rule.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert InstanceRule.select().count() == 0


@pytest.mark.integration
def test_delete_instance_rule_already_deleted(client, g_user, journey):
    response = client.delete("/observability/v1/instance-conditions/ff703df2-5831-4306-a4e3-d80e62d991b7")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json


@pytest.mark.integration
def test_delete_instance_rule_forbidden(client, g_user_2, instance_rule):
    assert InstanceRule.select().count() == 1
    response = client.delete(f"/observability/v1/instance-conditions/{instance_rule.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert InstanceRule.select().count() == 1


@pytest.mark.integration
def test_create_instance_rule_with_batch_pipeline(client, g_user, journey, pipeline):
    assert InstanceRule.select().count() == 0
    response = client.post(
        f"/observability/v1/journeys/{journey.id}/instance-conditions",
        headers={"Content-Type": "application/json"},
        json={"action": "START", "batch_pipeline": pipeline.id},
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert InstanceRule.select().count() == 1

    data = response.json
    assert "START" == data["action"]
    assert str(journey.id) == data["journey"]
    assert str(pipeline.id) == data["batch_pipeline"]
    assert data["schedule"] is None
    assert all(k not in ["expression", "timezone"] for k in data.keys())


@pytest.mark.integration
@pytest.mark.parametrize(
    "invalid_data",
    [
        {"batch_pipeline": None, "schedule": None},
        {"batch_pipeline": str(uuid.uuid4()), "schedule": {"expression": "* * * * *"}},
        {"batch_pipeline": ""},
    ],
)
def test_create_instance_rule_invalid_input(invalid_data, client, g_user, journey):
    data = {"action": InstanceRuleAction.START.name}
    data.update(invalid_data)
    response = client.post(
        f"/observability/v1/journeys/{journey.id}/instance-conditions",
        headers={"Content-Type": "application/json"},
        json=data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    assert InstanceRule.select().count() == 0


@pytest.mark.integration
def test_create_instance_rule_with_schedule(client, g_user, journey, instance_rule_schedule_data):
    assert InstanceRule.select().count() == 0
    response = client.post(
        f"/observability/v1/journeys/{journey.id}/instance-conditions",
        headers={"Content-Type": "application/json"},
        json={"action": "START", "schedule": instance_rule_schedule_data},
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert InstanceRule.select().count() == 1

    data = response.json
    assert "START" == data["action"]
    assert str(journey.id) == data["journey"]
    assert data["batch_pipeline"] is None
    assert data["schedule"]["expression"] == instance_rule_schedule_data["expression"]
    assert data["schedule"]["timezone"] == instance_rule_schedule_data["timezone"]
    assert all(k not in ["expression", "timezone"] for k in data.keys())


@pytest.mark.integration
def test_create_instance_rule_no_journey(client, g_user, pipeline):
    assert InstanceRule.select().count() == 0
    response = client.post(
        "/observability/v1/journeys/e421a297-a740-4869-a5d0-5ff20aa4c51f/instance-conditions",
        headers={"Content-Type": "application/json"},
        json={"action": "START", "batch_pipeline": pipeline.id},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_create_instance_rule_forbidden(client, g_user_2, journey, pipeline):
    assert InstanceRule.select().count() == 0
    response = client.post(
        f"/observability/v1/journeys/{journey.id}/instance-conditions",
        headers={"Content-Type": "application/json"},
        json={"action": "START", "batch_pipeline": pipeline.id},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
