from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from common.entities import Agent
from common.entities.agent import AgentStatus
from scheduler.agent_check import _update_agent_status

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
def test_check_agents_are_online(project, agents, agent_source):
    with patch("scheduler.agent_check._update_agent_status") as update_mock:
        agent_source._check_agents_are_online(project)

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


@pytest.mark.integration
def test_id_changes_when_interval_changes(agent_source, project):
    schedules_1 = agent_source._get_schedules()
    id_list_1 = [s.id for s in schedules_1]

    schedules_2 = agent_source._get_schedules()
    id_list_2 = [s.id for s in schedules_2]

    project.agent_check_interval += 10
    project.save()

    schedules_3 = agent_source._get_schedules()
    id_list_3 = [s.id for s in schedules_3]

    assert len(id_list_1) == 1
    assert len(id_list_3) == 1
    assert id_list_1 == id_list_2
    assert id_list_3 != id_list_1
