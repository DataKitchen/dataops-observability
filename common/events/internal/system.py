__all__ = ("AgentStatusChangeEvent", "ProjectAlertEvent")

from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

from common.entities.agent import AgentStatus
from common.events.base import EventBaseMixin, ProjectMixin


@dataclass(kw_only=True)
class ProjectAlertEvent(EventBaseMixin, ProjectMixin):
    pass


@dataclass(kw_only=True)
class AgentStatusChangeEvent(ProjectAlertEvent):
    agent_id: UUID
    agent_key: str
    agent_tool: str
    previous_status: AgentStatus
    current_status: AgentStatus
    latest_heartbeat: datetime
    latest_event_timestamp: datetime
