import copy
from uuid import UUID, uuid4

import pytest

from common.entities import (
    Dataset,
    Instance,
    InstanceRule,
    InstanceRuleAction,
    InstanceSet,
    InstancesInstanceSets,
    InstanceStatus,
    Journey,
    JourneyDagEdge,
    Run,
    RunStatus,
)
from common.entities.instance import InstanceStartType
from common.events.base import InstanceRef, InstanceType
from run_manager.run_manager import RunManager


@pytest.mark.integration
def test_run_manager_payload_instance_create_new(
    kafka_consumer,
    kafka_producer,
    run_status_message,
    project,
    pipeline,
    journey,
    pipeline_edge,
    pipeline_end_payload_rule,
):
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = pipeline.key
    run_status_message.payload.payload_keys = ["p1", "p2"]
    assert Instance.select().count() == 0

    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 3

    assert kafka_producer.produce.call_count == 1
    output_event1 = kafka_producer.produce.call_args_list[0][0][1]
    results = list(Instance.select().order_by(Instance.payload_key))
    for actual, expected in zip(results, output_event1.instances):
        assert (
            InstanceRef(
                journey=actual.journey.id,
                instance=actual.id,
                instance_type=InstanceType.PAYLOAD if actual.payload_key else InstanceType.DEFAULT,
            )
            == expected
        )
    assert results[1].payload_key == "p1"
    assert results[1].start_type == InstanceStartType.PAYLOAD
    assert results[2].payload_key == "p2"
    assert results[2].start_type == InstanceStartType.PAYLOAD


@pytest.mark.integration
def test_run_manager_payload_instance_reuse_existed(
    kafka_consumer, kafka_producer, run_status_message, project, pipeline, journey, pipeline_end_payload_rule
):
    Instance.create(journey=journey, payload_key=pipeline.key)
    Instance.create(journey=journey)
    run_status_message.payload.pipeline_key = pipeline.key
    run_status_message.payload.payload_keys = [pipeline.key]
    assert Instance.select().count() == 2

    run_status_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 2

    assert kafka_producer.produce.call_count == 1
    output_event1 = kafka_producer.produce.call_args_list[0][0][1]
    results = list(Instance.select().order_by(Instance.payload_key))
    for actual, expected in zip(results, output_event1.instances):
        assert (
            InstanceRef(
                journey=actual.journey.id,
                instance=actual.id,
                instance_type=InstanceType.PAYLOAD if actual.payload_key else InstanceType.DEFAULT,
            )
            == expected
        )
    assert results[1].payload_key == pipeline.key


@pytest.mark.integration
def test_run_manager_close_payload_instances_on_pipeline_completion(
    kafka_consumer,
    kafka_producer,
    run_status_message,
    completed_run_message,
    journey,
    pipeline,
    pipeline2,
    simple_dag,
    pipeline_end_payload_rule,
):
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.payload_keys = ["p1", "p2"]
    run_status_message2 = copy.deepcopy(run_status_message)
    run_status_message2.payload.event_id = uuid4()
    run_status_message2.payload.pipeline_key = pipeline2.key
    run_status_message2.payload.run_key = "pipeline2-run"
    run_status_message2.payload.payload_keys = ["p3"]
    kafka_consumer.__iter__.return_value = iter((run_status_message, run_status_message2))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = Instance.select()
    assert len(instances) == 4
    assert all(instance.active is True for instance in instances)
    assert Run.select().count() == 2

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 4
    # Should close all payload instances that are related to `pipeline`'s run
    # (despite event is sent with payload key `p1` only)
    instances = list(Instance.select().where(Instance.active == False))
    assert len(instances) == 2
    assert [instance.payload_key for instance in instances] == ["p1", "p2"]

    # Regular instance and payload instance from `pipeline2` remain active
    instances = list(Instance.select().where(Instance.active == True))
    assert len(instances) == 2
    assert [instance.payload_key for instance in instances] == [None, "p3"]


@pytest.mark.integration
def test_run_manager_close_payload_instances_on_schedule(
    kafka_consumer,
    kafka_producer,
    instance_end_payload_msg,
    journey,
    pipeline,
    pipeline_edge,
    project,
    timestamp_now,
    timestamp_past,
):
    Instance.create(journey=journey, start_time=timestamp_past)
    payload_instance = Instance.create(journey=journey, start_time=timestamp_now, payload_key=pipeline.key)

    assert Instance.select().where(Instance.active == True).count() == 2

    kafka_consumer.__iter__.return_value = iter((instance_end_payload_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Instance rule END_PAYLOAD action only affects payload instances
    instances = list(Instance.select().order_by(Instance.start_time))
    assert len(instances) == 2
    assert instances[0].active is True
    assert instances[0].payload_key is None
    assert instances[1].end_time == instance_end_payload_msg.payload.timestamp
    assert instances[1].id == payload_instance.id
    assert instances[1].payload_key == pipeline.key


@pytest.mark.integration
def test_run_manager_payload_instance_disabled(
    kafka_consumer, kafka_producer, run_status_message, journey, simple_dag, pipeline
):
    # If payload instance is disabled, i.e. journey has no END_PAYLOAD rule, do not create payload instances
    # even if the event is sent with payload keys
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = pipeline.key
    run_status_message.payload.payload_keys = [pipeline.key]
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 1
    assert Run.select().count() == 1
    assert Instance.get().payload_key is None


@pytest.mark.integration
def test_run_manager_one_payload_key_multiple_journeys(
    kafka_consumer, kafka_producer, completed_run_message, run_status_message, pipeline, pipeline2, project
):
    journey = Journey.create(id=UUID(int=1), name="journey1", project=project)
    JourneyDagEdge.create(journey=journey, right=pipeline)
    InstanceRule.create(journey=journey, action=InstanceRuleAction.END_PAYLOAD, batch_pipeline=pipeline)
    journey2 = Journey.create(id=UUID(int=2), name="journey2", project=project)
    JourneyDagEdge.create(journey=journey2, left=pipeline, right=pipeline2)
    InstanceRule.create(journey=journey2, action=InstanceRuleAction.END_PAYLOAD, batch_pipeline=pipeline2)

    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = pipeline.key
    run_status_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Sorted by journey first, then default instance, payload instance
    instances = list(Instance.select().order_by(Instance.journey, Instance.payload_key.asc(nulls="FIRST")))
    # Should create one default instance and one payload instance for each journey
    assert len(instances) == 4
    assert all(instance.active is True for instance in instances)
    assert Run.select().count() == 1

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = pipeline.key
    completed_run_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Should close only default instance and payload instance of journey1
    inactive_instances = list(
        Instance.select()
        .where(Instance.active == False)
        .order_by(Instance.journey, Instance.payload_key.asc(nulls="FIRST"))
    )
    assert len(inactive_instances) == 2
    for actual, expected in zip(inactive_instances, instances[:1]):
        assert (actual.id, actual.journey, actual.payload_key) == (expected.id, expected.journey, expected.payload_key)

    # Default instance and payload instance of journey2 should still be active
    active_instances = list(
        Instance.select()
        .where(Instance.active == True)
        .order_by(Instance.journey, Instance.payload_key.asc(nulls="FIRST"))
    )
    assert len(active_instances) == 2
    for actual, expected in zip(active_instances, instances[2:]):
        assert (actual.id, actual.journey, actual.payload_key) == (expected.id, expected.journey, expected.payload_key)


@pytest.mark.integration
def test_run_manager_ignore_new_payload_keys_on_existed_run(
    kafka_consumer,
    kafka_producer,
    completed_run_message,
    run_status_message,
    journey,
    pipeline,
    pipeline_edge,
    pipeline_end_payload_rule,
):
    run_status_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = list(Instance.select())
    assert len(instances) == 2
    assert all(instance.active is True for instance in instances)
    assert [i.payload_key for i in instances] == [None, "p1"]

    run_status_message2 = copy.deepcopy(run_status_message)
    run_status_message2.payload.payload_keys = ["p1", "p2"]
    kafka_consumer.__iter__.return_value = iter((run_status_message2,))

    run_manager.process_events()

    # Run already existed -> don't create a new payload instance `p2`
    instances = list(Instance.select())
    assert len(instances) == 2
    assert [i.payload_key for i in instances] == [None, "p1"]


@pytest.mark.integration
def test_run_manager_payload_instance_non_run_status_event_type(
    kafka_consumer,
    kafka_producer,
    journey,
    pipeline,
    pipeline_edge,
    pipeline_end_payload_rule,
    message_log_message,
    run_status_message,
    test_outcomes_message,
):
    run_status_message.payload.payload_keys = ["p1", "p2"]
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = list(Instance.select())
    assert len(instances) == 3
    assert Run.select().count() == 1
    assert InstanceSet.select().count() == 1
    for instance, payload_key in zip(instances, [None, "p1", "p2"]):
        assert instance.active is True
        assert instance.payload_key == payload_key

    message_log_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((message_log_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = list(Instance.select())
    assert len(instances) == 3
    assert Run.select().count() == 1
    # Reuse all the run's instances regardless of what payload_keys is sent -> no new instance set created
    assert InstanceSet.select().count() == 1

    test_outcomes_message.payload.payload_keys = ["p2"]
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = list(Instance.select())
    assert len(instances) == 3
    assert Run.select().count() == 1
    assert InstanceSet.select().count() == 1
    # Run's instance set should reference all 3 instances
    assert set(iis.instance for iis in Run.get().instance_set.iis) == set(instances)


@pytest.mark.integration
def test_run_manager_payload_instance_start_with_non_run_status_event(
    kafka_consumer,
    kafka_producer,
    journey,
    pipeline,
    pipeline_edge,
    pipeline_end_payload_rule,
    completed_run_message,
    metric_log_message,
):
    metric_log_message.payload.event_id = uuid4()
    metric_log_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((metric_log_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = list(Instance.select())
    assert len(instances) == 2
    assert Run.select().where(Run.status == RunStatus.RUNNING.value).count() == 1
    assert [i.payload_key for i in instances] == [None, "p1"]

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.payload_keys = ["p1", "p2"]
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager.process_events()

    # If run already exists, don't create new instances on subsequent events
    instances = list(Instance.select())
    assert len(instances) == 2
    assert [i.payload_key for i in instances] == [None, "p1"]
    assert Run.select().count() == 1
    # Run and instances should be closed
    assert Run.get().status == RunStatus.COMPLETED.value
    assert all(instance.active is False for instance in instances)


@pytest.mark.integration
def test_run_manager_dataset_operation_event_with_payload_keys(
    kafka_consumer,
    kafka_producer,
    journey,
    dataset,
    mixed_dag,
    pipeline_end_payload_rule,
    completed_run_message,
    dataset_operation_message,
):
    dataset_operation_message.payload.event_id = uuid4()
    dataset_operation_message.payload.dataset_key = dataset.key
    dataset_operation_message.payload.payload_keys = ["file1"]
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.payload_keys = ["file1", "p1"]
    kafka_consumer.__iter__.return_value = iter((dataset_operation_message, completed_run_message))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    instances = list(Instance.select())
    assert len(instances) == 3
    for instance in instances:
        assert instance.payload_key in [None, "file1", "p1"]
        assert instance.status == InstanceStatus.COMPLETED.value
    assert Dataset.select().count() == 1
    assert Run.select().count() == 1
    assert Run.get().status == RunStatus.COMPLETED.value


@pytest.mark.integration
def test_run_manager_batch_start_rule_dont_affect_payload_instances(
    kafka_consumer,
    kafka_producer,
    journey,
    pipeline,
    pipeline2,
    simple_dag,
    pipeline_end_payload_rule,
    completed_run_message,
    running_run_message,
    test_outcomes_message,
    instance_start_msg,
):
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, batch_pipeline=pipeline2)
    assert Instance.select().count() == 0

    instance_start_msg.payload.event_id = uuid4()
    instance_start_msg.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((instance_start_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Instance rule START should not create payload instance
    assert Instance.select().count() == 1
    assert Run.select().count() == 0
    reg_instance_1 = Instance.get()

    test_outcomes_message.payload.event_id = uuid4()
    test_outcomes_message.payload.payload_keys = ["p1"]
    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # A run is created for the first time -> reuse the existing regular instance and create a new payload instance `p1`
    instances = list(Instance.select())
    assert len(instances) == 2
    assert reg_instance_1.id in [instance.id for instance in instances]
    assert all(instance.active is True for instance in instances)
    assert Run.select().count() == 1

    running_run_message.payload.event_id = uuid4()
    running_run_message.payload.pipeline_key = pipeline2.key
    kafka_consumer.__iter__.return_value = iter((running_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Instance START rule ends currently active regular instance
    inactive_instances = list(Instance.select().where(Instance.active == False))
    assert len(inactive_instances) == 1
    assert inactive_instances[0].id == reg_instance_1.id
    assert Run.select().count() == 2

    active_instances = list(Instance.select().where(Instance.active == True))
    assert len(active_instances) == 2

    # Payload instance is not affect by instance START rule
    assert active_instances[0].payload_key == "p1"

    # All instances of pipeline2 run should be the existing payload instance `p1` and a new regular instance,
    # i.e. not `reg_instance_1` above
    pipeline2_run = Run.select().where(Run.pipeline == pipeline2).prefetch(InstanceSet, InstancesInstanceSets, Instance)
    assert all(iis.instance == active_instances[1] for run in pipeline2_run for iis in run.instance_set.iis)
