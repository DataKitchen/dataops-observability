import operator

import pytest
from http import HTTPStatus

from common.entities import Action, ActionImpl
from testlib.fixtures.entities import *


@pytest.fixture
def actions(company):
    return [
        Action.create(name="Action_1", company=company, action_impl=ActionImpl.CALL_WEBHOOK),
        Action.create(name="Action_2", company=company, action_impl=ActionImpl.CALL_WEBHOOK),
        Action.create(name="Action_3", company=company, action_impl=ActionImpl.SEND_EMAIL),
    ]


@pytest.mark.integration
def test_list_actions(client, company, g_user, actions):
    response = client.get(f"/observability/v1/companies/{company.id!s}/actions")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 3
    assert data["total"] == 3


@pytest.mark.integration
def test_list_actions_forbidden(client, company, g_user_2, actions):
    response = client.get(f"/observability/v1/companies/{company.id!s}/actions")

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_actions_impl_search(client, company, g_user, actions):
    response = client.get(
        f"/observability/v1/companies/{company.id!s}/actions", query_string={"action_impl": "CALL_WEBHOOK"}
    )

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["total"] == 2
    assert data["entities"][0]["action_impl"] == "CALL_WEBHOOK"


@pytest.mark.integration
@pytest.mark.parametrize("sort,test_op", (("asc", operator.lt), ("desc", operator.gt)), ids=("asc", "desc"))
def test_list_actions_sort(sort, test_op, client, company, g_user, actions):
    response = client.get(f"/observability/v1/companies/{company.id!s}/actions", query_string={"sort": sort})

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["total"] == 3
    assert test_op(data["entities"][0]["name"], data["entities"][2]["name"])


@pytest.mark.integration
def test_patch_action(client, g_user, action):
    response = client.patch(
        f"/observability/v1/actions/{action.id!s}",
        headers={"Content-Type": "application/json"},
        json={"name": "new_name", "action_impl": "SEND_EMAIL"},
    )

    assert response.status_code == HTTPStatus.OK, response.json
    action_db = Action.get_by_id(action.id)
    assert action_db.name == "new_name"


@pytest.mark.integration
def test_patch_action_validation_error(client, g_user, action):
    response = client.patch(
        f"/observability/v1/actions/{action.id!s}", headers={"Content-Type": "application/json"}, json={}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_action_forbidden(client, g_user_2, action):
    response = client.patch(
        f"/observability/v1/actions/{action.id!s}", headers={"Content-Type": "application/json"}, json={}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
