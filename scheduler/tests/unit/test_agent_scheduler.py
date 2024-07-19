import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest
from apscheduler.triggers.interval import IntervalTrigger

from common.entities import Project
from common.entities.agent import AgentStatus
from scheduler.agent_status import _get_agent_status

CHECK_INTERVAL = 100


@pytest.mark.unit
def test_add_job(agent_source):
    project = Project(id=uuid.uuid4(), agent_status_check_interval=300)

    with patch.object(agent_source, "add_job") as add_mock:
        agent_source._create_and_add_job(project)

    print(add_mock.call_args_list)

    add_mock.assert_called_once()
    args = add_mock.call_args_list[0][0]
    assert args[0] == agent_source._check_agents_are_online
    assert args[1] == str(project.id)
    assert isinstance(args[2], IntervalTrigger)
    assert args[2].interval == timedelta(seconds=300)
    assert args[3] == {"project": project}


@pytest.mark.unit
@pytest.mark.parametrize(
    "elapsed_time, expected_status",
    [
        (1, AgentStatus.ONLINE),
        (199, AgentStatus.ONLINE),
        (200, AgentStatus.UNHEALTHY),
        (399, AgentStatus.UNHEALTHY),
        (400, AgentStatus.OFFLINE),
        (900, AgentStatus.OFFLINE),
    ],
)
def test_get_agent_status(elapsed_time, expected_status):
    latest_heartbeat = datetime.now(tz=timezone.utc) - timedelta(seconds=elapsed_time)
    assert _get_agent_status(CHECK_INTERVAL, latest_heartbeat) == expected_status
