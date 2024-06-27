from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from common.entities import Agent
from common.entities.agent import AgentStatus
from scheduler.agent_status import _check_agents_are_online

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
    with (
        patch("scheduler.agent_status.handle_agent_status_change", side_effect=(False, True, True)) as handler_mock,
        patch("common.entities.Agent.save") as save_mock,
    ):
        _check_agents_are_online(project)

    assert handler_mock.call_count == 3
    assert handler_mock.call_args_list[0][0][1] == AgentStatus.ONLINE
    assert handler_mock.call_args_list[1][0][1] == AgentStatus.UNHEALTHY
    assert handler_mock.call_args_list[2][0][1] == AgentStatus.OFFLINE
    assert save_mock.call_count == 2
