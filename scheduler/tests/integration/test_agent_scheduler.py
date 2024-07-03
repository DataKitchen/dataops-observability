from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from common.entities import Agent
from common.entities.agent import AgentStatus
from scheduler.agent_status import _check_agents_are_online, _update_agent_status

from testlib.fixtures.entities import *


@pytest.fixture
def agents(project):
    return [
        Agent.create(
            project=project,
            key=f"ag_{elapsed_time}",
            tool="tool",
            version="vTest",
            status=AgentStatus.ONLINE,
            latest_heartbeat=datetime.now(tz=timezone.utc) - timedelta(seconds=elapsed_time),
        )
        for elapsed_time in (
            25,  # Below the checking threshold
            32,  # Online
            90,  # Unhealthy
            170,  # Offline
        )
    ]


@pytest.mark.integration
def test_check_agents_are_online(project, agents):
    with patch("scheduler.agent_status._update_agent_status") as update_mock:
        _check_agents_are_online(project)

    assert update_mock.call_count == 2
    assert update_mock.call_args_list[0][0][1] == AgentStatus.UNHEALTHY
    assert update_mock.call_args_list[1][0][1] == AgentStatus.OFFLINE


@pytest.mark.integration
def test_update_agent_status_ok(agent_2):
    new_status = AgentStatus.UNHEALTHY

    ret = _update_agent_status(agent_2, new_status)

    assert ret, "_update_agent_status should return True on success"
    agent_from_db = Agent.get(Agent.id == agent_2.id)
    assert agent_from_db.status == new_status


@pytest.mark.integration
def test_update_agent_status_blocked(agent_2):
    new_status = AgentStatus.UNHEALTHY
    current_status = agent_2.status
    Agent.update(latest_heartbeat=agent_2.latest_heartbeat + timedelta(minutes=3)).execute()

    ret = _update_agent_status(agent_2, new_status)

    assert not ret, "_update_agent_status should return False when blocked"
    agent_from_db = Agent.get(Agent.id == agent_2.id)
    assert agent_from_db.status == current_status
