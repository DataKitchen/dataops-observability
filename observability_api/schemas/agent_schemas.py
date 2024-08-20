__all__ = ("AgentSchema",)

from marshmallow.fields import DateTime, String
from marshmallow.validate import Length

from common.entities import Agent
from common.entities.agent import AgentStatus
from common.schemas.fields import EnumStr

from .base_schemas import BaseEntitySchema


class AgentSchema(BaseEntitySchema):
    key = String(
        required=True, validate=Length(max=255), metadata={"description": "The identifier key given to the agent."}
    )
    tool = String(
        required=True, validate=Length(max=255), metadata={"description": "The tool the agent is integrating with."}
    )
    version = String(
        required=True, validate=Length(max=255), metadata={"description": "The version of the agent deployed."}
    )
    status = EnumStr(required=True, enum=AgentStatus, metadata={"description": "Agent connectivity status."})
    latest_heartbeat = DateTime(
        required=True,
        metadata={
            "description": "The UTC timestamp of the latest heartbeat received by Observability from the agent.",
        },
    )
    latest_event_timestamp = DateTime(
        required=False,
        dump_default=None,
        metadata={
            "description": "The UTC timestamp that the agent last reported an event was sent to observability.",
        },
    )

    class Meta:
        model = Agent
