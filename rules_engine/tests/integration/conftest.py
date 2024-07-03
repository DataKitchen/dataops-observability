from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest

from common.entities import (
    Action,
    ActionImpl,
    AlertLevel,
    InstanceAlertType,
    JourneyDagEdge,
    Pipeline,
    Rule,
    RunState,
    RunStatus,
)
from common.events.enums import EventSources
from common.events.v1 import ApiRunStatus, RunStatusEvent, TestOutcomesEvent, TestStatuses
from common.kafka import TOPIC_IDENTIFIED_EVENTS, KafkaMessage
from rules_engine.actions.action_factory import ACTION_CLASS_MAP
from rules_engine.rules import _get_rules
from testlib.fixtures.entities import *
from testlib.fixtures.v2_events import *


@pytest.fixture
def base_event_data():
    return {
        "pipeline_key": None,
        "pipeline_name": None,
        "project_id": str(uuid4()),
        "source": EventSources.API.name,
        "event_timestamp": str(datetime.now(timezone.utc)),
        "received_timestamp": str(datetime.now(timezone.utc)),
        "external_url": "https://example.com",
        "metadata": {},
        "run_id": None,
        "run_key": None,
        "pipeline_id": None,
        "task_id": None,
        "task_key": None,
        "task_name": None,
        "run_task_id": None,
    }


@pytest.fixture
def kafka_consumer() -> MagicMock:
    kafka_consumer = MagicMock()
    yield kafka_consumer


@pytest.fixture
def components(project, pipeline, pipeline_2):
    pipeline_3 = Pipeline.create(key="Pipeline-3", project=project)
    pipeline_4 = Pipeline.create(key="Pipeline-4", project=project)
    pipeline_5 = Pipeline.create(key="Pipeline-5", project=project)
    return (pipeline, pipeline_2, pipeline_3, pipeline_4, pipeline_5)


@pytest.fixture
def journey_dag(journey, journey_2, components):
    p1, p2, p3, p4, p5 = components
    yield [
        JourneyDagEdge.create(journey=journey, left=p1, right=p2),
        JourneyDagEdge.create(journey=journey, left=p2, right=p3),
        JourneyDagEdge.create(journey=journey, left=p3, right=p4),
        # P1 is shared in J1 and J2
        JourneyDagEdge.create(journey=journey_2, left=p1, right=p5),
    ]


@pytest.fixture
def action(company):
    action = Action.create(name="action1", company=company, action_impl=ActionImpl.CALL_WEBHOOK.value)
    yield action


@pytest.fixture
def db_rule(journey, pipeline, action):
    _get_rules.cache_clear()
    rule = Rule.create(
        action=action.action_impl,
        component=pipeline,
        journey=journey,
        rule_schema="simple_v1",
        rule_data={
            "when": "all",
            "conditions": [
                {"task_status": {"matches": RunStatus.RUNNING.name}},
            ],
        },
    )
    yield rule


@pytest.fixture
def instance_alert_rule(journey, pipeline, action):
    _get_rules.cache_clear()
    rule = Rule.create(
        action=action.action_impl,
        component=pipeline,
        journey=journey,
        rule_schema="simple_v1",
        rule_data={
            "when": "all",
            "conditions": [
                {
                    "instance_alert": {
                        "level_matches": [AlertLevel.WARNING.value],
                        "type_matches": [InstanceAlertType.INCOMPLETE.value],
                    }
                }
            ],
        },
    )
    yield rule


@pytest.fixture
def run_state_rule(journey, pipeline, action, dag_simple):
    _get_rules.cache_clear()
    rule = Rule.create(
        action=action.action_impl,
        component=pipeline,
        journey=journey,
        rule_schema="simple_v1",
        rule_data={
            "when": "all",
            "conditions": [
                {
                    "run_state": {
                        "matches": RunState.LATE_START.value,
                    }
                }
            ],
        },
    )
    yield rule


@pytest.fixture
def run_status_event(base_event_data, task, pipeline, journey, journey_2):
    data = {
        "event_type": RunStatusEvent.__name__,
        "task_key": "a task key",
        "task_name": "a task name",
        "status": ApiRunStatus.RUNNING.name,
        "task_id": task.id,
        "pipeline_key": pipeline.key,
        "run_key": pipeline.key,
        "pipeline_id": pipeline.id,
        "instances": [{"instance": uuid4(), "journey": journey.id}, {"instance": uuid4(), "journey": journey_2.id}],
    }
    return KafkaMessage(
        payload=RunStatusEvent(**RunStatusEvent.__schema__().load({**base_event_data, **data})),
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={},
    )


@pytest.fixture
def test_outcome_event_data(journey, journey_2):
    data = {
        "event_type": TestOutcomesEvent.__name__,
        "test_outcomes": [{"name": "n", "status": TestStatuses.PASSED.name, "description": "d"}],
        "instances": [{"instance": uuid4(), "journey": journey.id}, {"instance": uuid4(), "journey": journey_2.id}],
        "external_url": "https://example.com",
    }
    return data


@pytest.fixture
def batch_pipeline_test_outcome_event_message(
    base_event_data, test_outcome_event_data, task, pipeline, journey, journey_2
):
    batch_pipeline_data = {
        "task_key": "a task key",
        "task_name": "a task name",
        "task_id": task.id,
        "pipeline_key": pipeline.key,
        "run_key": pipeline.key,
        "pipeline_id": pipeline.id,
    }
    return KafkaMessage(
        payload=TestOutcomesEvent(
            **TestOutcomesEvent.__schema__().load({**base_event_data, **test_outcome_event_data, **batch_pipeline_data})
        ),
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={},
    )


@pytest.fixture
def dataset_test_outcome_event_message(test_outcome_event_data, base_event_data, dataset):
    dataset_data = {"dataset_id": dataset.id, "dataset_key": dataset.key}
    return KafkaMessage(
        payload=TestOutcomesEvent(
            **TestOutcomesEvent.__schema__().load({**base_event_data, **test_outcome_event_data, **dataset_data})
        ),
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={},
    )


@pytest.fixture
def server_test_outcome_event_message(test_outcome_event_data, base_event_data, server):
    server_data = {"server_id": server.id, "server_key": server.key}
    return KafkaMessage(
        payload=TestOutcomesEvent(
            **TestOutcomesEvent.__schema__().load({**base_event_data, **test_outcome_event_data, **server_data})
        ),
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={},
    )


@pytest.fixture
def streaming_pipeline_test_outcome_event_message(test_outcome_event_data, base_event_data, stream):
    streaming_pipeline_data = {"stream_id": stream.id, "stream_key": stream.key}
    return KafkaMessage(
        payload=TestOutcomesEvent(
            **TestOutcomesEvent.__schema__().load(
                {**base_event_data, **test_outcome_event_data, **streaming_pipeline_data}
            )
        ),
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={},
    )


@pytest.fixture
def fake_action_class(action):
    action_entity = Mock()
    action_class = Mock(return_value=action_entity)
    with patch.dict(ACTION_CLASS_MAP, values={action.action_impl: action_class}):
        yield action_class


@pytest.fixture
def internal_event_instance_alert_message(instance_alert):
    return KafkaMessage(
        payload=instance_alert,
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={"Content-Type": "application/msgpack"},
    )


@pytest.fixture
def internal_event_run_alert_message(run_alert):
    return KafkaMessage(
        payload=run_alert,
        topic=TOPIC_IDENTIFIED_EVENTS.name,
        partition=2,
        offset=1,
        headers={"Content-Type": "application/msgpack"},
    )
