from unittest.mock import Mock, patch

import pytest

from common.agent import handle_agent_status_change
from common.entities.agent import AgentStatus, Agent


parametrize_status_changes = pytest.mark.parametrize(
    "expected_res,status",
    ((True, AgentStatus.ONLINE), (False, AgentStatus.UNHEALTHY), (True, AgentStatus.OFFLINE)),
)


@pytest.mark.unit
@parametrize_status_changes
def test_agent_status_change_handler(expected_res, status):
    agent = Agent(status=AgentStatus.UNHEALTHY)

    res = handle_agent_status_change(agent, status)

    assert res == expected_res
    assert agent.status == status


@pytest.mark.unit
@parametrize_status_changes
def test_agent_status_change_handler_with_watchers(expected_res, status):
    agent = Agent(status=AgentStatus.UNHEALTHY)
    watchers = (
        Mock(),
        Mock(side_effect=Exception("Crashed")),  # One watcher crashing shouldn't affect the subsequent watchers
        Mock(),
    )

    with patch("common.agent.AGENT_STATUS_WATCHERS", new=watchers):
        res = handle_agent_status_change(agent, status)

    assert res == expected_res
    assert agent.status == status

    for watcher in watchers:
        if res:
            assert watcher.call_count == 1
            assert watcher.call_args_list[0][0][0] == agent
            assert watcher.call_args_list[0][0][1] == status
        else:
            assert watcher.call_count == 0
