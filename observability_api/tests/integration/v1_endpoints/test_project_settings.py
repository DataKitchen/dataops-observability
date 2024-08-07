import pytest
from http import HTTPStatus

from common.entities import Project
from testlib.fixtures.entities import *


@pytest.fixture
def base_patch_data():
    return {
        "agent_check_interval": 60,
        "actions": [
            {
                "action_impl": "SEND_EMAIL",
                "action_args": {"recipients": ["example@domain.com"], "template": "alert_template"},
            }
        ],
    }


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
def test_patch_alert_settings(client, g_user, project, action, base_patch_data):
    response = client.patch(
        f"/observability/v1/projects/{project.id!s}/alert-settings",
        headers={"Content-Type": "application/json"},
        json=base_patch_data,
    )

    assert response.status_code == HTTPStatus.OK, response.json
    project_db = Project.get_by_id(project.id)
    assert project_db.agent_check_interval == 60
    assert project_db.alert_actions[0]["action_impl"] == "SEND_EMAIL"


@pytest.mark.integration
@pytest.mark.parametrize(
    "patch_data",
    (
        {"actions": [{"wrong_arg": "x"}]},
        {"actions": [{"action_impl": "DO_NOTHING"}]},
        {"actions": [{"action_impl": "SEND_EMAIL"}]},
        {"actions": [{"action_impl": "SEND_EMAIL", "action_args": {"recipients": ["x@dom.com"]}}]},
        {"actions": [{"action_impl": "CALL_WEBHOOK", "action_args": {"method": "POST"}}]},
        {"agent_check_interval": 29},
        {"agent_check_interval": 24 * 60 * 60 + 1},
    ),
    ids=(
        "invalid-action-fields",
        "invalid-action_impl",
        "missing-action-args",
        "send-email-template-missing",
        "webhook-url-missing",
        "min-check-interval",
        "max-check-interval",
    ),
)
def test_patch_alert_settings_validation_error(patch_data, client, g_user, project, base_patch_data, action):
    response = client.patch(
        f"/observability/v1/projects/{project.id!s}/alert-settings",
        headers={"Content-Type": "application/json"},
        json={**base_patch_data, **patch_data},
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
