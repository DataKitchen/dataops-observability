__all__ = ["handle_agent_status_change"]

import logging
from typing import Callable

from common.entities import Agent
from common.entities.agent import AgentStatus
from common.plugins import PluginManager

LOG = logging.getLogger(__name__)

AGENT_STATUS_WATCHERS: list[Callable[[Agent, AgentStatus], None]] = []

PluginManager.load_all("agent_status_watcher", AGENT_STATUS_WATCHERS)


def handle_agent_status_change(agent: Agent, status: AgentStatus) -> bool:
    if agent.status != status:
        LOG.info(
            "Agent '%s' status changed from %s to %s. Propagating to %d watchers",
            agent.id,
            agent.status,
            status,
            len(AGENT_STATUS_WATCHERS),
        )
        for watcher in AGENT_STATUS_WATCHERS:
            try:
                watcher(agent, status)
            except Exception:
                LOG.exception("Agent status change watcher failed.")
        agent.status = status  # type: ignore[assignment]
        return True
    else:
        LOG.debug("Agent '%s' status did not change: %s", agent.id, agent.status)
        return False
