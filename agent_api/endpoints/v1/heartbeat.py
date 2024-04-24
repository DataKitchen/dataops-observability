import logging
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional, Union, cast
from uuid import UUID

from boltons.cacheutils import LRI
from flask import Response, g, make_response
from peewee import DoesNotExist
from werkzeug.exceptions import BadRequest

from agent_api.schemas.heartbeat import HeartbeatSchema
from common.api.base_view import BaseView
from common.entities import Agent
from common.hash import generate_key
from common.peewee_extensions.fields import UTCTimestampField
from common.sentinel import SENTINEL, Sentinel

LOG = logging.getLogger(__name__)
UTC = timezone.utc
HEARTBEAT_SCHEMA = HeartbeatSchema()
AGENT_CACHE = LRI(max_size=512)
"""
A cache of registered observability Agent instances.

A proper update_or_create cannot be done with MySQL. MySQL doesn't support on_conflict on an update. It does support it
for insert, but this deletes the row and recreates it which defeats the efficiency gains and breaks relationships.

By caching Agent instances we can dispatch updates; if an Agent has been previously cached then we assume we
can perform an update. If it hasn't been cached, THEN we do a traditional get_or_create and then update the value(s).
This means that there is one extra round-trip to the database everytime max-requests is hit or when we get a request
for an agent instance that has been evicted from the cache.
"""


def _update_or_create(
    *,
    key: str,
    tool: str,
    version: str,
    project_id: Union[str, UUID],
    latest_heartbeat: datetime,
    latest_event_timestamp: Optional[datetime],
) -> None:
    cache_key = generate_key(key, tool, project_id)
    agent: Union[Sentinel, Agent] = AGENT_CACHE.get(cache_key, default=SENTINEL)
    if agent is SENTINEL:
        try:
            retrieved_agent = (
                Agent.select().where(Agent.key == key, Agent.tool == tool, Agent.project_id == project_id).get()
            )
        except DoesNotExist:
            new_agent = Agent(
                key=key,
                tool=tool,
                version=version,
                project_id=project_id,
                latest_heartbeat=latest_heartbeat,
                latest_event_timestamp=latest_event_timestamp,
            )
            new_agent.save(force_insert=True)
            AGENT_CACHE[cache_key] = new_agent
        else:
            retrieved_agent.latest_heartbeat = cast(UTCTimestampField, latest_heartbeat)
            # Only set if changed so it doesn't always get flagged as "dirty"
            if retrieved_agent.version != version:
                retrieved_agent.version = version

            if retrieved_agent.latest_event_timestamp != latest_event_timestamp:
                retrieved_agent.latest_event_timestamp = cast(UTCTimestampField, latest_event_timestamp)

            retrieved_agent.save()
            AGENT_CACHE[cache_key] = retrieved_agent  # Update the cached value
    elif isinstance(agent, Agent):
        agent.latest_heartbeat = cast(UTCTimestampField, latest_heartbeat)
        if agent.version != version:
            agent.version = version

        if agent.latest_event_timestamp != latest_event_timestamp:
            agent.latest_event_timestamp = cast(UTCTimestampField, latest_event_timestamp)
        agent.save()
        AGENT_CACHE[cache_key] = agent  # Update the cached value
    else:
        raise BadRequest(f"Invalid Agent value: {agent}")


class Heartbeat(BaseView):
    """Agent heartbeat."""

    PERMISSION_REQUIREMENTS = ()

    def post(self) -> Response:
        data = self.parse_body(schema=HEARTBEAT_SCHEMA)
        data["latest_heartbeat"] = datetime.now(UTC)
        data["project_id"] = g.project.id
        _update_or_create(**data)
        return make_response("", HTTPStatus.NO_CONTENT)
