import pytest

from common.entities import Instance, InstanceAlert, InstanceAlertType, InstanceSet, JourneyDagEdge, Pipeline
from common.entities.instance import InstanceStartType, InstanceStatus
from common.events.internal import InstanceAlert as InstanceAlertEvent
from run_manager.run_manager import RunManager


@pytest.mark.integration
def test_instance_start_rule(
    kafka_producer, kafka_consumer, instance_start_msg, timestamp_now, timestamp_past, ended_instance
):
    Instance.create(journey=ended_instance.journey, start_time=timestamp_past, end_time=timestamp_now)
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 0

    kafka_consumer.__iter__.return_value = iter((instance_start_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Start a new instance
    assert Instance.select().count() == 3
    instance = Instance.select().where(Instance.active == True)
    assert len(instance) == 1
    assert instance[0].start_type == InstanceStartType.SCHEDULED


@pytest.mark.integration
def test_instance_start_rule_active_instance_found(
    kafka_producer, kafka_consumer, instance_start_msg, timestamp_now, timestamp_past, ended_instance
):
    Instance.create(journey=ended_instance.journey, start_time=timestamp_past)

    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 1

    kafka_consumer.__iter__.return_value = iter((instance_start_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # End currently active instance then start a new one
    assert Instance.select().count() == 3
    assert Instance.select().where(Instance.active == True).count() == 1


@pytest.mark.integration
def test_instance_end_rule(
    kafka_producer, kafka_consumer, instance_end_msg, timestamp_now, timestamp_past, ended_instance
):
    Instance.create(journey=ended_instance.journey, start_time=timestamp_past, end_time=timestamp_now)
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 0

    kafka_consumer.__iter__.return_value = iter((instance_end_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # No active instance found -> do nothing
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 0


@pytest.mark.integration
def test_instance_end_rule_active_instance_found(
    kafka_producer, kafka_consumer, instance_end_msg, timestamp_now, timestamp_past, ended_instance
):
    Instance.create(journey=ended_instance.journey, start_time=timestamp_past)
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 1

    kafka_consumer.__iter__.return_value = iter((instance_end_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # End currently active instance
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 0


@pytest.mark.integration
def test_instance_end_rule_with_incomplete_instance(
    kafka_producer, kafka_consumer, instance_end_msg, timestamp_past, journey, instance, project
):
    pipeline = Pipeline.create(project=project, key="p")
    JourneyDagEdge.create(journey=journey, right=pipeline)
    InstanceSet.get_or_create([instance.id])
    assert Instance.select().where(Instance.active == True).count() == 1

    kafka_consumer.__iter__.return_value = iter((instance_end_msg,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert kafka_producer.produce.call_count == 1
    produced_event = kafka_producer.produce.call_args_list[0][0][1]
    assert isinstance(produced_event, InstanceAlertEvent)
    assert produced_event.type == InstanceAlertType.INCOMPLETE

    assert Instance.select().where(Instance.active == True).count() == 0
    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.type == InstanceAlertType.INCOMPLETE
    assert alert.instance == instance
    assert Instance.select().count() == 1
    assert alert.instance.has_warnings is False
    assert alert.instance.has_errors is True
    assert alert.instance.status == InstanceStatus.ERROR.value
