import pytest
from http import HTTPStatus

from common.entities import Project
from testlib.fixtures.entities import *


@pytest.mark.integration
def test_get_alerts_settings(client, project, g_user):
    response = client.get(f"/observability/v1/projects/{project.id!s}/alert-settings")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data == {
        "agent_check_interval": 30,
        "actions": [
            {
                "action_impl": "CALL_WEBHOOK",
                "action_args": {
                    "url": "https://some.callback/url",
                    "headers": None,
                    "method": "POST",
                    "payload": None,
                },
            },
        ],
    }


@pytest.mark.integration
def test_get_alerts_settings_forbidden(client, project, g_user_2):
    response = client.get(f"/observability/v1/projects/{project.id!s}/alert-settings")

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_patch_alert_settings(client, g_user, project):
    response = client.patch(
        f"/observability/v1/projects/{project.id!s}/alert-settings",
        headers={"Content-Type": "application/json"},
        json={"agent_check_interval": 60, "actions": [{"action_impl": "SEND_EMAIL"}]},
    )

    assert response.status_code == HTTPStatus.OK, response.json
    project_db = Project.get_by_id(project.id)
    assert project_db.agent_status_check_interval == 60
    assert project_db.alert_actions[0]["action_impl"] == "SEND_EMAIL"


@pytest.mark.integration
def test_patch_alert_settings_validation_error(client, g_user, project):
    response = client.patch(
        f"/observability/v1/projects/{project.id!s}/alert-settings",
        headers={"Content-Type": "application/json"},
        json={"agent_check_interval": 60, "actions": [{"wrong_arg": "x"}]},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_alert_settings_forbidden(client, g_user_2, project):
    response = client.patch(
        f"/observability/v1/projects/{project.id!s}/alert-settings",
        headers={"Content-Type": "application/json"},
        json={},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
