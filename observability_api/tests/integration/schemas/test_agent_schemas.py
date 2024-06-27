from uuid import UUID

import pytest

from observability_api.schemas import AgentSchema
from testlib.fixtures import entities

project_entity = entities.project
agent_1_entity = entities.agent_1


@pytest.mark.unit
def test_agent_dump(agent_1_entity):
    data = AgentSchema().dump(agent_1_entity)

    assert "test-agent-1-key" == data["key"]
    assert agent_1_entity.latest_heartbeat.isoformat() == data["latest_heartbeat"]
    assert agent_1_entity.latest_event_timestamp.isoformat() == data["latest_event_timestamp"]
    assert "OFFLINE" == data["status"]
    assert "1.0.0" == data["version"]
    assert "test-agent-1-tool" == data["tool"]

    try:
        UUID(data["id"])
    except Exception:
        raise AssertionError(f"ID {data['id']} is not a valid UUID")
