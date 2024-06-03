import pytest
from http import HTTPStatus

from testlib.fixtures import entities

agent_1 = entities.agent_1
agent_2 = entities.agent_2


@pytest.mark.integration
def test_list_agents(client, project, g_user, agent_1, agent_2):
    response = client.get(f"/observability/v1/projects/{project.id!s}/agents")
    assert HTTPStatus.OK == response.status_code, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert 2 == data["total"]


@pytest.mark.integration
def test_list_agents_forbidden(client, project, g_user_2, agent_1, agent_2):
    response = client.get(f"/observability/v1/projects/{project.id!s}/agents")
    assert HTTPStatus.FORBIDDEN == response.status_code, response.json


@pytest.mark.integration
def test_list_agents_key_search(client, project, g_user, agent_1, agent_2):
    search = client.get(f"/observability/v1/projects/{project.id!s}/agents", query_string={"search": "agent-2-key"})
    assert HTTPStatus.OK == search.status_code, search.json
    data = search.json
    assert 1 == data["total"]
    agent_data = data["entities"][0]
    assert "test-agent-2-key" == agent_data["key"]


@pytest.mark.integration
def test_list_agents_tool_search(client, project, g_user, agent_1, agent_2):
    search = client.get(f"/observability/v1/projects/{project.id!s}/agents", query_string={"search": "agent-2-tool"})
    assert HTTPStatus.OK == search.status_code, search.json
    data = search.json
    assert 1 == data["total"]
    agent_data = data["entities"][0]
    assert "test-agent-2-tool" == agent_data["tool"]


@pytest.mark.integration
def test_list_agents_sort_ascending(client, project, g_user, agent_1, agent_2):
    response = client.get(f"/observability/v1/projects/{project.id!s}/agents", query_string={"sort": "asc"})
    assert HTTPStatus.OK == response.status_code, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert 2 == data["total"]

    _agent_1 = data["entities"][0]
    _agent_2 = data["entities"][1]

    assert _agent_1["latest_heartbeat"] < _agent_2["latest_heartbeat"]


@pytest.mark.integration
def test_list_agents_sort_descending(client, project, g_user, agent_1, agent_2):
    response = client.get(f"/observability/v1/projects/{project.id!s}/agents", query_string={"sort": "desc"})
    assert HTTPStatus.OK == response.status_code, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert 2 == data["total"]

    _agent_1 = data["entities"][0]
    _agent_2 = data["entities"][1]

    assert _agent_1["latest_heartbeat"] > _agent_2["latest_heartbeat"]
