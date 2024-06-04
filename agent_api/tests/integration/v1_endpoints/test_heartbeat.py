from datetime import datetime, timezone
from http import HTTPStatus

import pytest

from agent_api.endpoints.v1.heartbeat import AGENT_CACHE
from common.entities import Agent


def _reset_agent_cache():
    AGENT_CACHE.clear()
    AGENT_CACHE.miss_count = 0
    AGENT_CACHE.soft_miss_count = 0
    AGENT_CACHE.hit_count = 0


@pytest.fixture(autouse=True)
def reset_agent_cache():
    """Reset the agent cache between test invocations."""
    _reset_agent_cache()


@pytest.mark.integration
def test_agent_heartbeat(client, database_ctx, headers):
    assert 0 == AGENT_CACHE.miss_count
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=timezone.utc)
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response.status_code, response.json
    assert 1 == AGENT_CACHE.miss_count


@pytest.mark.integration
def test_agent_heartbeat_no_event_timestamp(client, database_ctx, headers):
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
    }
    response = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response.status_code, response.json
    agent = Agent.select().get()
    assert agent.latest_event_timestamp is None


@pytest.mark.integration
def test_agent_heartbeat_update(client, database_ctx, headers):
    assert 0 == AGENT_CACHE.miss_count
    assert 0 == AGENT_CACHE.hit_count
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=timezone.utc)
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    assert 0 == Agent.select().count()  # Initially there should be no registered agents
    response_1 = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json
    assert (
        1 == AGENT_CACHE.miss_count
    ), f"Expected 1 cache miss after first call to heartbeat, got {AGENT_CACHE.miss_count}"
    assert (
        0 == AGENT_CACHE.hit_count
    ), f"Expected 0 cache hits after first call to heartbeat, got {AGENT_CACHE.hit_count}"

    # The latest_event_timestamp should be older than "now"
    now = datetime.now(timezone.utc)
    agent_1 = Agent.select().get()
    assert agent_1.latest_heartbeat < now

    # We hit the API again so now latest_event_timestamp should be newer than "now"
    response_2 = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    agent_2 = Agent.select().get()
    assert agent_2.latest_heartbeat > now
    assert (
        1 == AGENT_CACHE.miss_count
    ), f"Expected 1 cache miss after second call to heartbeat, got {AGENT_CACHE.miss_count}"
    assert (
        1 == AGENT_CACHE.hit_count
    ), f"Expected 1 cache hit after second call to heartbeat, got {AGENT_CACHE.hit_count}"


@pytest.mark.integration
def test_agent_heartbeat_existing_no_cache(client, database_ctx, headers):
    assert 0 == AGENT_CACHE.miss_count
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=timezone.utc)
    data = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "test-version",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response_1 = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json
    assert 1 == AGENT_CACHE.miss_count
    assert 1 == Agent.select().count()  # There should be 1 agent now

    now = datetime.now(timezone.utc)
    _reset_agent_cache()  # Clear the cache again
    response_2 = client.post("/agent/v1/heartbeat", json=data, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    assert 1 == AGENT_CACHE.miss_count
    assert 1 == Agent.select().count()  # There should still be only 1 agent
    agent = Agent.select().get()
    assert agent.latest_heartbeat > now  # The latest_heartbeat should be newer than "now"


@pytest.mark.integration
def test_agent_heartbeat_existing_version_update(client, database_ctx, headers):
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=timezone.utc)
    data_1 = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "0.1.0",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response_1 = client.post("/agent/v1/heartbeat", json=data_1, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json

    agent_1 = Agent.select().get()

    data_2 = data_1.copy()
    data_2["version"] = "12.0.3"

    response_2 = client.post("/agent/v1/heartbeat", json=data_2, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    assert 1 == Agent.select().count()  # There should still be only 1 agent
    agent_2 = Agent.select().get()
    assert "12.0.3" == agent_2.version, "Agent version should have been updated to `12.0.3`"
    assert agent_1.version != agent_2.version, "Expected agent version to change"


@pytest.mark.integration
def test_agent_heartbeat_update_no_cache(client, database_ctx, headers):
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=timezone.utc)
    data_1 = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "0.1.0",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response_1 = client.post("/agent/v1/heartbeat", json=data_1, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json

    agent_1 = Agent.select().get()

    data_2 = data_1.copy()
    data_2["version"] = "12.0.3"
    data_2["latest_event_timestamp"] = datetime(2023, 10, 20, 4, 44, 44, tzinfo=timezone.utc).isoformat()

    _reset_agent_cache()  # Clear the cache before updating
    response_2 = client.post("/agent/v1/heartbeat", json=data_2, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    assert 1 == Agent.select().count()  # There should still be only 1 agent
    agent_2 = Agent.select().get()
    assert "12.0.3" == agent_2.version, "Agent version should have been updated to `12.0.3`"
    assert agent_1.version != agent_2.version, "Expected agent version to change"


@pytest.mark.integration
def test_agent_heartbeat_update_with_cache(client, database_ctx, headers):
    last_event_timestamp = datetime(2023, 10, 20, 4, 42, 42, tzinfo=timezone.utc)
    data_1 = {
        "key": "test-key",
        "tool": "test-tool",
        "version": "0.1.0",
        "latest_event_timestamp": last_event_timestamp.isoformat(),
    }
    response_1 = client.post("/agent/v1/heartbeat", json=data_1, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_1.status_code, response_1.json

    agent_1 = Agent.select().get()

    data_2 = data_1.copy()
    data_2["version"] = "1.0.3"
    data_2["latest_event_timestamp"] = datetime(2023, 10, 20, 4, 44, 44, tzinfo=timezone.utc).isoformat()

    response_2 = client.post("/agent/v1/heartbeat", json=data_2, headers=headers)
    assert HTTPStatus.NO_CONTENT == response_2.status_code, response_2.json
    assert 1 == Agent.select().count()  # There should still be only 1 agent
    agent_2 = Agent.select().get()
    assert "1.0.3" == agent_2.version, "Agent version should have been updated to `1.0.3`"
    assert agent_1.version != agent_2.version, "Expected agent version to change"
