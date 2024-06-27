from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from common.entities import ScheduleExpectation
from common.events.enums import ScheduleType
from scheduler.agent_status import AgentStatusScheduleSource
from scheduler.component_expectations import ComponentScheduleSource
from scheduler.instance_expectations import InstanceScheduleSource


@pytest.fixture
def scheduler():
    return Mock()


@pytest.fixture
def event_producer_mock():
    return Mock()


@pytest.fixture
def component_source(scheduler, event_producer_mock):
    with patch.object(ComponentScheduleSource, "update"):
        return ComponentScheduleSource(scheduler, event_producer_mock)


@pytest.fixture
def instance_rule_source(scheduler, event_producer_mock):
    with patch.object(InstanceScheduleSource, "update"):
        return InstanceScheduleSource(scheduler, event_producer_mock)


@pytest.fixture
def agent_source(scheduler, event_producer_mock):
    with patch.object(AgentStatusScheduleSource, "update"):
        return AgentStatusScheduleSource(scheduler, event_producer_mock)


@pytest.fixture
def job_kwargs():
    return {
        "run_time": datetime.now(tz=timezone.utc),
        "schedule_type": ScheduleType.BATCH_END_TIME,
        "schedule_id": str(uuid4()),
        "component_id": str(uuid4()),
        "margin": None,
        "is_margin": False,
    }


@pytest.fixture
def schedule_data():
    return {
        "id": str(uuid4()),
        "component": str(uuid4()),
        "expectation": ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
        "schedule": "* * * * *",
        "margin": 10,
    }


@pytest.fixture
def run_time():
    return datetime.now(tz=timezone.utc)
