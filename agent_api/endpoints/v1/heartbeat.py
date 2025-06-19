import logging
from datetime import datetime, UTC
from http import HTTPStatus
from typing import Union, cast
from uuid import UUID

from flask import Response, g, make_response
from peewee import DoesNotExist

from agent_api.schemas.heartbeat import HeartbeatSchema
from common.api.base_view import BaseView
from common.entities import Agent
from common.entities.agent import AgentStatus
from common.peewee_extensions.fields import UTCTimestampField

LOG = logging.getLogger(__name__)


def _update_or_create(
    *,
    key: str,
    tool: str,
    version: str,
    project_id: Union[str, UUID],
    latest_heartbeat: datetime,
    latest_event_timestamp: datetime | None,
) -> None:
    try:
        agent = Agent.select().where(Agent.key == key, Agent.tool == tool, Agent.project_id == project_id).get()
    except DoesNotExist:
        agent = Agent(
            key=key,
            tool=tool,
            version=version,
            project_id=project_id,
            status=AgentStatus.ONLINE,
            latest_heartbeat=latest_heartbeat,
            latest_event_timestamp=latest_event_timestamp,
        )
        agent.save(force_insert=True)

    agent.latest_heartbeat = cast(UTCTimestampField, latest_heartbeat)
    # Only set if changed, so it doesn't always get flagged as "dirty"
    if agent.version != version:
        agent.version = version
    if agent.latest_event_timestamp != latest_event_timestamp:
        agent.latest_event_timestamp = cast(UTCTimestampField, latest_event_timestamp)
    if agent.status != AgentStatus.ONLINE:
        agent.status = AgentStatus.ONLINE
    agent.save()


class Heartbeat(BaseView):
    """Agent heartbeat."""

    PERMISSION_REQUIREMENTS = ()

    def post(self) -> Response:
        data = self.parse_body(schema=HeartbeatSchema())
        data["latest_heartbeat"] = datetime.now(tz=UTC)
        data["project_id"] = g.project.id
        _update_or_create(**data)
        return make_response("", HTTPStatus.NO_CONTENT)
