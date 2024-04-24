import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from peewee import SqliteDatabase

from common.entities import (
    ALL_MODELS,
    Company,
    Dataset,
    Instance,
    InstanceRule,
    InstanceRuleAction,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Organization,
    Pipeline,
    Project,
    Run,
    RunStatus,
    Server,
    StreamingPipeline,
)
from common.events.internal import ScheduledInstance
from common.events.v1 import (
    ApiRunStatus,
    MessageEventLogLevel,
    MessageLogEvent,
    MetricLogEvent,
    RunStatusEvent,
    TestOutcomesEvent,
    TestStatuses,
)
from common.kafka import TOPIC_SCHEDULED_EVENTS, TOPIC_UNIDENTIFIED_EVENTS, KafkaMessage
from conf import init_db
from testlib.fixtures.entities import patched_instance_set, pending_run  # noqa: F401
from testlib.fixtures.v1_events import *


def compare_event_data(unidentified_event, identified_event, pipeline, run, task=None, run_task=None):
    assert unidentified_event.payload.pipeline_key == identified_event.pipeline_key
    assert unidentified_event.payload.pipeline_key == pipeline.key
    assert unidentified_event.payload.project_id == identified_event.project_id
    assert unidentified_event.payload.project_id == pipeline.project_id
    assert unidentified_event.payload.pipeline_id == pipeline.id
    assert unidentified_event.payload.run_id == run.id
    assert unidentified_event.payload.run_key == run.key
    if task:
        assert unidentified_event.payload.task_id == task.id
    if run_task:
        assert unidentified_event.payload.run_task_id == run_task.id


@pytest.fixture
def timestamp_now():
    return datetime.now(tz=timezone.utc)


@pytest.fixture
def timestamp_future(timestamp_now):
    return timestamp_now + timedelta(seconds=60)


@pytest.fixture
def timestamp_past(timestamp_now):
    return timestamp_now - timedelta(seconds=60)


@pytest.fixture
def test_db():
    init_db()

    # Keep memory db alive between Run Manager consumed messages by opening a
    # second db connection
    sqlite = SqliteDatabase(
        "file:cachedb?mode=memory&cache=shared",
        pragmas={"foreign_keys": 1},
        uri=True,
    )
    sqlite.connect()
    yield sqlite
    sqlite.close()


@pytest.fixture(autouse=True)
def test_base(test_db):
    test_db.create_tables(ALL_MODELS)
    yield
    test_db.drop_tables(ALL_MODELS)


@pytest.fixture(autouse=True)
def local_patched_instance_set(patched_instance_set):
    yield patched_instance_set


# TODO: Replace with actual Kafka service instead of mock
@pytest.fixture
def kafka_producer() -> MagicMock:
    class ProduceStore:
        def __init__(self):
            self.store = []

        def __call__(self, topic, event):
            self.store.append(replace(event))

    kafka_producer = MagicMock()
    kafka_producer.__enter__.return_value = kafka_producer
    # RunManager produces the same event instance with different run_ids.
    # Custom storage is needed to for copying the instances so earlier calls
    # aren't lost
    kafka_producer.produce.side_effect = ProduceStore()
    yield kafka_producer


# TODO: Replace with actual Kafka service instead of mock
@pytest.fixture
def kafka_consumer() -> MagicMock:
    kafka_consumer = MagicMock()
    yield kafka_consumer


@pytest.fixture
def project():
    company = Company.create(name="company1")
    organization = Organization.create(name="org1", company=company)
    project = Project.create(name="proj1", organization=organization, id=project_id)
    return project


@pytest.fixture
def journey(project):
    return Journey.create(name="journey1", project=project)


@pytest.fixture
def instance(journey):
    return Instance.create(journey=journey)


@pytest.fixture()
def ended_instance(journey, timestamp_now):
    return Instance.create(journey=journey, end_time=timestamp_now)


@pytest.fixture
def instance_instance_set(instance):
    return InstancesInstanceSets.create(instance=instance, instance_set=InstanceSet.create())


@pytest.fixture
def pipeline(project):
    pipeline = Pipeline.create(key=pipeline_key, project=project, id=pipeline_id)
    return pipeline


@pytest.fixture
def pipeline_edge(journey, pipeline):
    return JourneyDagEdge.create(journey=journey, right=pipeline)


@pytest.fixture
def pipeline2(project):
    pipeline = Pipeline.create(key=pipeline_key + "2", project=project, id=uuid.uuid4())
    return pipeline


@pytest.fixture
def simple_dag(journey, pipeline, pipeline2):
    return JourneyDagEdge.create(journey=journey, left=pipeline, right=pipeline2)


@pytest.fixture
def mixed_dag(journey, pipeline, dataset, server, stream):
    for component in [dataset, server, stream]:
        JourneyDagEdge.create(journey=journey, left=component, right=pipeline)
    return JourneyDagEdge.get()


@pytest.fixture
def dataset(project):
    dataset = Dataset.create(key="dataset key", project=project)
    return dataset


@pytest.fixture
def dataset_edge(journey, dataset):
    return JourneyDagEdge.create(journey=journey, right=dataset)


@pytest.fixture
def server(project):
    server = Server.create(key="server key", project=project)
    return server


@pytest.fixture
def stream(project):
    streaming_pipeline = StreamingPipeline.create(key="stream key", project=project)
    return streaming_pipeline


@pytest.fixture
def run(pipeline):
    return Run.create(id=run_id, key=run_key, pipeline=pipeline, status=RunStatus.RUNNING.name)


@pytest.fixture()
def instance_rule_start(journey):
    return InstanceRule.create(
        journey=journey, action=InstanceRuleAction.START, expression="* * * * *", timezone="America/New_York"
    )


@pytest.fixture()
def instance_rule_end(journey):
    return InstanceRule.create(
        journey=journey, action=InstanceRuleAction.END, expression="* * * * *", timezone="America/New_York"
    )


@pytest.fixture()
def instance_rule_end_payload(journey):
    return InstanceRule.create(
        journey=journey, action=InstanceRuleAction.END_PAYLOAD, expression="* * * * *", timezone="America/New_York"
    )


@pytest.fixture
def running_run_message(RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = None
    return KafkaMessage(
        payload=RUNNING_run_status_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def completed_run_message(COMPLETED_run_status_event):
    COMPLETED_run_status_event.pipeline_id = None
    return KafkaMessage(
        payload=COMPLETED_run_status_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def message_log_event(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy["log_level"] = MessageEventLogLevel.WARNING.name
    data_copy["message"] = "some message"
    message_log = MessageLogEvent.as_event_from_request(data_copy)
    message_log.project_id = project.id
    return message_log


@pytest.fixture
def message_log_message(message_log_event):
    return KafkaMessage(
        payload=message_log_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def metric_log_event(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy["metric_key"] = "metric key"
    data_copy["metric_value"] = 10.0
    metric_log = MetricLogEvent.as_event_from_request(data_copy)
    metric_log.project_id = project.id
    return metric_log


@pytest.fixture
def metric_log_message(metric_log_event):
    return KafkaMessage(
        payload=metric_log_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def run_status_event(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy["status"] = ApiRunStatus.RUNNING.name
    status = RunStatusEvent.as_event_from_request(data_copy)
    status.project_id = project.id
    return status


@pytest.fixture
def run_status_event_pending(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy["status"] = ApiRunStatus.RUNNING.name  # Required for marshmallow, but not an api event
    status = RunStatusEvent.as_event_from_request(data_copy)
    status.project_id = project.id
    status.status = RunStatus.PENDING.name  # Make this a pending event
    status.metadata["expected_start_time"] = 1109638861.0
    return status


@pytest.fixture
def run_status_event_missing(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy["status"] = ApiRunStatus.RUNNING.name  # Required for marshmallow, but not an api event
    status = RunStatusEvent.as_event_from_request(data_copy)
    status.project_id = project.id
    status.status = RunStatus.MISSING.name  # Make this a missing event
    status.metadata["expected_start_time"] = 1109638861.0
    return status


@pytest.fixture
def run_status_message(run_status_event):
    return KafkaMessage(
        payload=run_status_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def task_status_event(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy["task_key"] = "a task key"
    data_copy["status"] = ApiRunStatus.RUNNING.name
    status = RunStatusEvent.as_event_from_request(data_copy)
    status.project_id = project.id
    return status


@pytest.fixture
def task_status_message(task_status_event):
    return KafkaMessage(
        payload=task_status_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def test_outcomes_event(unidentified_event_data, project):
    data_copy = unidentified_event_data.copy()
    data_copy.pop("pipeline_name", None)
    test_outcomes_data = {"test_outcomes": [{"name": "n", "status": TestStatuses.PASSED.name, "description": "d"}]}
    test_outcomes_data.update(data_copy)
    test_outcome = TestOutcomesEvent.as_event_from_request(test_outcomes_data)
    test_outcome.project_id = project.id
    return test_outcome


@pytest.fixture
def test_outcomes_message(test_outcomes_event):
    return KafkaMessage(
        payload=test_outcomes_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def dataset_operation_message(dataset_operation_event):
    return KafkaMessage(
        payload=dataset_operation_event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={}
    )


@pytest.fixture
def pipeline_end_payload_rule(journey, pipeline):
    return InstanceRule.create(journey=journey, action=InstanceRuleAction.END_PAYLOAD, batch_pipeline=pipeline)


@pytest.fixture
def timestamp_now():
    return datetime.now(tz=timezone.utc)


@pytest.fixture
def timestamp_future(timestamp_now):
    return timestamp_now + timedelta(seconds=60)


@pytest.fixture
def timestamp_past(timestamp_now):
    return timestamp_now - timedelta(seconds=60)


@pytest.fixture
def scheduler_kafka_message_base():
    return {
        "topic": TOPIC_SCHEDULED_EVENTS.name,
        "partition": 2,
        "offset": 1,
        "headers": {},
    }


@pytest.fixture
def instance_start_msg(scheduler_kafka_message_base, instance_rule_start, timestamp_now):
    """Scheduled instance event with START action type"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledInstance(
            project_id=instance_rule_start.journey.project.id,
            journey_id=instance_rule_start.journey.id,
            instance_rule_id=instance_rule_start.id,
            instance_rule_action=instance_rule_start.action,
            timestamp=timestamp_now,
        ),
    )


@pytest.fixture
def instance_end_msg(scheduler_kafka_message_base, instance_rule_end, timestamp_now):
    """Scheduled instance event with END action type"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledInstance(
            project_id=instance_rule_end.journey.project.id,
            journey_id=instance_rule_end.journey.id,
            instance_rule_id=instance_rule_end.id,
            instance_rule_action=instance_rule_end.action,
            timestamp=timestamp_now,
        ),
    )


@pytest.fixture
def instance_end_payload_msg(scheduler_kafka_message_base, instance_rule_end_payload, timestamp_now):
    """Scheduled event with END_PAYLOAD action type"""
    return KafkaMessage(
        **scheduler_kafka_message_base,
        payload=ScheduledInstance(
            project_id=instance_rule_end_payload.journey.project.id,
            journey_id=instance_rule_end_payload.journey.id,
            instance_rule_id=instance_rule_end_payload.id,
            instance_rule_action=instance_rule_end_payload.action,
            timestamp=timestamp_now,
        ),
    )
