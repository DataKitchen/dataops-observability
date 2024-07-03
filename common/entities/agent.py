__all__ = ["Agent"]

from enum import Enum

from peewee import CharField, ForeignKeyField

from common.peewee_extensions.fields import UTCTimestampField, EnumStrField

from .base_entity import BaseEntity
from .project import Project


class AgentStatus(Enum):
    ONLINE = "ONLINE"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class Agent(BaseEntity):
    """A registered agent."""

    key = CharField(null=False)
    tool = CharField(null=False)
    version = CharField(null=False)
    project = ForeignKeyField(Project, backref="agents", on_delete="CASCADE", null=False, index=True)
    status = EnumStrField(AgentStatus, max_length=20, null=False)
    latest_heartbeat = UTCTimestampField(null=True, defaults_to_now=True)
    latest_event_timestamp = UTCTimestampField(null=True)

    class Meta:
        indexes = (
            # Unique index across key + tool + project id
            (("key", "tool", "project_id"), True),
        )
        table_name = "agent"
