import copy
from datetime import datetime, timezone, UTC
from uuid import uuid4

import pytest

from common.entities import (
    Dataset,
    Instance,
    InstanceAlert,
    InstanceAlertType,
    InstanceRule,
    InstanceRuleAction,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Run,
    RunStatus,
)
from common.entities.instance import InstanceStartType
from common.events.base import InstanceRef
from common.events.internal import InstanceAlert as InstanceAlertEvent
from common.events.v1 import RunStatusEvent
from run_manager.run_manager import RunManager


@pytest.mark.integration
def test_run_manager_close_instances(
    kafka_consumer, kafka_producer, run_status_message, project, pipeline, completed_run_message
):
    for i in range(4):
        journey = Journey.create(name=f"journey{i}", project=project)
        JourneyDagEdge.create(journey=journey, right=pipeline)
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = pipeline.key
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = pipeline.key
    kafka_consumer.__iter__.return_value = iter(
        (
            run_status_message,
            completed_run_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Instance.select().count() == 4
    assert Instance.select().where(Instance.active == False).count() == 4
    assert all(i.start_type == InstanceStartType.DEFAULT for i in Instance.select())

    assert kafka_producer.produce.call_count == 2
    output_event1 = kafka_producer.produce.call_args_list[0][0][1]
    output_event2 = kafka_producer.produce.call_args_list[1][0][1]
    for instance in Instance.select():
        assert InstanceRef(journey=instance.journey.id, instance=instance.id) in output_event1.instances
        assert InstanceRef(journey=instance.journey.id, instance=instance.id) in output_event2.instances


@pytest.mark.integration
def test_run_manager_close_instances_w_rule(
    kafka_consumer, kafka_producer, run_status_message, project, pipeline, completed_run_message
):
    for i in range(4):
        journey = Journey.create(name=f"journey{i}", project=project)
        InstanceRule.create(journey=journey, action=InstanceRuleAction.START, batch_pipeline=pipeline)
        InstanceRule.create(journey=journey, action=InstanceRuleAction.END, batch_pipeline=pipeline)
        JourneyDagEdge.create(journey=journey, right=pipeline)
    assert InstanceRule.select().count() == 8, "Expected there to have been 8 instance rules created"
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = pipeline.key
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = pipeline.key

    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # After processing the run status event, 4 instances should have had their start time set
    instances = Instance.select().where(Instance.start_time.is_null(False))
    assert len(instances) == 4
    assert all(i.start_type == InstanceStartType.BATCH for i in instances)

    # Invoke the run manager again, this time with a completed run event
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Instance.select().count() == 4
    # After processing the close run event, all 4 should be inactive again
    assert Instance.select().where(Instance.active == False).count() == 4

    assert kafka_producer.produce.call_count == 2
    output_event1 = kafka_producer.produce.call_args_list[0][0][1]
    output_event2 = kafka_producer.produce.call_args_list[1][0][1]
    for instance in Instance.select():
        assert InstanceRef(journey=instance.journey.id, instance=instance.id) in output_event1.instances
        assert InstanceRef(journey=instance.journey.id, instance=instance.id) in output_event2.instances


@pytest.mark.integration
def test_run_manager_restart_instance_w_rule(kafka_consumer, kafka_producer, run_status_message, project):
    j1 = Journey.create(name="journey1", project=project)
    j2 = Journey.create(name="journey2", project=project)
    i1 = Instance.create(journey=j1)
    i2 = Instance.create(journey=j2)
    p1 = Pipeline.create(key="pipe1", project=project)
    p2 = Pipeline.create(key="pipe2", project=project)
    JourneyDagEdge.create(journey=j1, left=p1, right=p2)
    JourneyDagEdge.create(journey=j2, left=p1, right=p2)
    InstanceRule.create(journey=j1, action=InstanceRuleAction.START, batch_pipeline=p1)
    run = Run.create(
        pipeline=p1,
        instance_set=InstanceSet.get_or_create([i1.id, i2.id]),
        key=uuid4(),
        end_time=datetime.utcnow(),
        status=RunStatus.RUNNING.name,
    )
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_id = None
    run_status_message.payload.pipeline_key = p1.key

    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().count() == 3
    assert Instance.get_by_id(i1).active is False
    assert Instance.get_by_id(i2).active is True
    new_instance = Instance.select().where(Instance.id.not_in((i1, i2))).get()
    assert new_instance.active is True
    assert Run.select().count() == 2
    # RunManager temporarily assigns an empty InstanceSet to the new Runs
    assert InstanceSet.select().count() == 2


@pytest.mark.integration
def test_run_manager_instance_not_finished(
    kafka_consumer, kafka_producer, run_status_message, project, journey, completed_run_message
):
    p1 = Pipeline.create(key="pipe1", project=project)
    JourneyDagEdge.create(journey=journey, right=p1)

    # Second pipeline that does not have a run in the instance
    p2 = Pipeline.create(key="pipe2", project=project)
    JourneyDagEdge.create(journey=journey, right=p2)

    run_status_message.payload.pipeline_id = None
    run_status_message.payload.pipeline_key = p1.key
    completed_run_message.payload.pipeline_id = None
    completed_run_message.payload.pipeline_key = p1.key
    kafka_consumer.__iter__.return_value = iter(
        (
            run_status_message,
            completed_run_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Instance.select().count() == 1
    assert Instance.select().where(Instance.active == False).count() == 0


@pytest.mark.integration
def test_run_manager_close_one_instance(
    kafka_consumer, kafka_producer, run_status_message, project, completed_run_message
):
    p1 = Pipeline.create(key="pipe1", project=project)
    p2 = Pipeline.create(key="pipe2", project=project)
    j1 = Journey.create(name="journey1", project=project)
    j2 = Journey.create(name="journey2", project=project)
    JourneyDagEdge.create(journey=j1, right=p1)
    JourneyDagEdge.create(journey=j2, right=p1)
    JourneyDagEdge.create(journey=j2, right=p2)

    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_id = None
    run_status_message.payload.pipeline_key = p1.key
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_id = None
    completed_run_message.payload.pipeline_key = p1.key
    kafka_consumer.__iter__.return_value = iter(
        (
            run_status_message,
            completed_run_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == False).count() == 1

    assert kafka_producer.produce.call_count == 2
    output_event1 = kafka_producer.produce.call_args_list[0][0][1]
    output_event2 = kafka_producer.produce.call_args_list[1][0][1]
    for instance in Instance.select():
        assert InstanceRef(journey=instance.journey.id, instance=instance.id) in output_event1.instances
        assert InstanceRef(journey=instance.journey.id, instance=instance.id) in output_event2.instances


@pytest.mark.integration
def test_run_manager_instance_two_runs_one_pipeline(
    kafka_consumer, kafka_producer, run_status_message, project, journey, completed_run_message
):
    assert Instance.select().count() == 0
    p1 = Pipeline.create(key="pipe1", project=project)
    p2 = Pipeline.create(key="pipe2", project=project)
    JourneyDagEdge.create(journey=journey, right=p1)
    JourneyDagEdge.create(journey=journey, left=p1, right=p2)

    # Remove the pipeline_id before copying the message payloads
    run_status_message.payload.pipeline_id = None
    completed_run_message.payload.pipeline_id = None

    p2_run_status_message = copy.deepcopy(run_status_message)
    p2_run_status_message.payload.event_id = uuid4()
    p2_completed_run_message = copy.deepcopy(completed_run_message)
    p2_completed_run_message.payload.event_id = uuid4()
    p2_run_status_message.payload.pipeline_key = p2.key
    p2_completed_run_message.payload.pipeline_key = p2.key
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = p1.key
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = p1.key
    run_status_message2 = copy.deepcopy(run_status_message)
    run_status_message2.payload.event_id = uuid4()
    run_status_message2.payload.pipeline_key = p1.key
    run_status_message2.payload.run_key = uuid4()
    kafka_consumer.__iter__.return_value = iter(
        (
            run_status_message,  # Start Run1 for Pipeline1
            p2_run_status_message,  # Start Run2 for Pipeline2
            completed_run_message,  # End Run1
            run_status_message2,  # Start Run3 for Pipeline1
            p2_completed_run_message,  # End Run2 (should end instance)
            run_status_message2,  # Continue Run3 in closed instance
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 3
    assert Instance.select().count() == 1
    assert Instance.select().where(Instance.active == False).count() == 1


@pytest.mark.integration
def test_run_manager_dont_modify_previously_closed_instance(
    kafka_consumer, kafka_producer, run_status_message, project, completed_run_message
):
    p1 = Pipeline.create(key="pipe1", project=project)
    j1 = Journey.create(name="journey1", project=project)
    instance_time = datetime.utcnow().replace(tzinfo=UTC)
    i1 = Instance.create(journey=j1, start_time=instance_time, end_time=instance_time)
    InstanceRule.create(journey=j1, action=InstanceRuleAction.START, batch_pipeline=p1)
    InstanceRule.create(journey=j1, action=InstanceRuleAction.END, batch_pipeline=p1)
    JourneyDagEdge.create(journey=j1, right=p1)

    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_id = None
    run_status_message.payload.pipeline_key = p1.key
    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_id = None
    completed_run_message.payload.pipeline_key = p1.key
    kafka_consumer.__iter__.return_value = iter(
        (
            run_status_message,
            completed_run_message,
        )
    )
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Instance.select().count() == 2
    i1 = Instance.get_by_id(i1.id)
    assert i1.start_time == instance_time
    assert i1.end_time == instance_time


@pytest.mark.integration
def test_close_two_instances_both_default_and_rule(kafka_consumer, kafka_producer, completed_run_message, project):
    run_key = uuid4()
    j1 = Journey.create(name="journey1", project=project)  # 1 pipeline, 0 rules
    j2 = Journey.create(name="journey2", project=project)  # 2 pipelines, 1 rule
    p1 = Pipeline.create(key="pipe1", project=project)
    p2 = Pipeline.create(key="pipe2", project=project)
    JourneyDagEdge.create(journey=j1, right=p2)
    JourneyDagEdge.create(journey=j2, left=p1, right=p2)
    InstanceRule.create(journey=j2, action=InstanceRuleAction.END, batch_pipeline=p2)
    i1 = Instance.create(journey=j1)
    i2 = Instance.create(journey=j2)
    Run.create(
        pipeline=p2, instance_set=InstanceSet.get_or_create([i1.id, i2.id]), key=run_key, status=RunStatus.RUNNING.name
    )

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_id = None
    completed_run_message.payload.pipeline_key = p2.key
    completed_run_message.payload.run_key = run_key

    # When p2's run end it should end both instances
    assert Instance.select().where(Instance.active == True).count() == 2
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Run.select().count() == 1
    assert Instance.select().count() == 2
    assert Instance.select().where(Instance.active == True).count() == 0


@pytest.mark.integration
def test_close_only_related_instances(
    kafka_consumer, kafka_producer, completed_run_message, run_status_message, project
):
    run_key = uuid4()
    j1 = Journey.create(name="journey1", project=project)  # 1 pipeline, 0 rules
    j2 = Journey.create(name="journey2", project=project)  # 2 pipelines, 1 rule
    p1 = Pipeline.create(key="pipe1", project=project)
    p2 = Pipeline.create(key="pipe2", project=project)
    JourneyDagEdge.create(journey=j1, right=p2)
    JourneyDagEdge.create(journey=j2, left=p1, right=p2)
    InstanceRule.create(journey=j2, action=InstanceRuleAction.END, batch_pipeline=p2)

    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_id = None
    run_status_message.payload.pipeline_key = p2.key
    run_status_message.payload.run_key = run_key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()
    assert Instance.select().where(Instance.active == True).count() == 2

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_id = None
    completed_run_message.payload.pipeline_key = p2.key
    completed_run_message.payload.run_key = run_key
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()
    assert Instance.select().where(Instance.active == True).count() == 0

    # A new run
    new_run_key = uuid4()
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = p2.key
    run_status_message.payload.run_key = new_run_key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().where(Instance.active == True).count() == 2
    assert Instance.select().count() == 4
    assert Run.select().count() == 2

    # Start and end the original run again
    run_status_message.payload.event_id = uuid4()
    run_status_message.payload.pipeline_key = p2.key
    run_status_message.payload.run_key = run_key
    kafka_consumer.__iter__.return_value = iter((run_status_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    completed_run_message.payload.event_id = uuid4()
    completed_run_message.payload.pipeline_key = p2.key
    completed_run_message.payload.run_key = run_key
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    # Now the original should have been closed but instances belonging to run2 should not have been closed. PD-1073
    assert Instance.select().where(Instance.active == True).count() == 2
    assert Instance.select().where(Instance.active == False).count() == 2
    assert Run.select().where(Run.key == new_run_key).count() == 1
    run_2 = Run.get(Run.key == new_run_key)
    assert (
        Instance.select()
        .join(InstancesInstanceSets)
        .join(InstanceSet)
        .join(Run)
        .where(Instance.active == True, Run.id == run_2.id)
    ).count() == 2


@pytest.mark.integration
def test_dataset_operation_instance_creation(kafka_consumer, kafka_producer, project, dataset_operation_message):
    assert Instance.select().count() == 0
    j = Journey.create(name="journey1", project=project)  # 1 pipeline, 0 rules
    d = Dataset.create(key=dataset_operation_message.payload.dataset_key, project=project)
    JourneyDagEdge.create(journey=j, right=d)

    dataset_operation_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((dataset_operation_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert Instance.select().where(Instance.active == True).count() == 1
    assert kafka_producer.produce.call_count == 1
    produced_event = kafka_producer.produce.call_args_list[0][0][1]
    assert produced_event.instances[0].journey == j.id
    assert produced_event.instances[0].instance == Instance.get().id
    assert produced_event.dataset_id == d.id


@pytest.mark.integration
def test_instance_with_rule_should_not_end_when_all_pipelines_finished(
    kafka_consumer,
    kafka_producer,
    completed_run_message,
    project,
    pipeline,
    journey,
    instance,
    pipeline_edge,
    instance_instance_set,
):
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, batch_pipeline=pipeline)
    Run.create(
        pipeline=pipeline,
        instance_set=instance_instance_set.instance_set,
        key=completed_run_message.payload.run_key,
        status=RunStatus.RUNNING.name,
    )
    assert instance.active is True

    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()
    assert Instance.select().where(Instance.active == True).count() == 1


@pytest.mark.integration
def test_end_incomplete_instance_with_rule(
    kafka_consumer, kafka_producer, project, completed_run_message, journey, instance
):
    p1 = Pipeline.create(key="some key", project=project)
    p2 = Pipeline.create(key=completed_run_message.payload.pipeline_key, project=project)
    InstanceRule.create(journey=journey, action=InstanceRuleAction.END, batch_pipeline=p2)
    JourneyDagEdge.create(journey=journey, right=p1)
    JourneyDagEdge.create(journey=journey, right=p2)
    iset = InstanceSet.get_or_create([instance])
    Run.create(pipeline=p1, key="key", instance_set=iset, status=RunStatus.RUNNING.name)

    assert Instance.select().where(Instance.active == True).count() == 1

    completed_run_message.payload.event_id = uuid4()
    kafka_consumer.__iter__.return_value = iter((completed_run_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)
    run_manager.process_events()

    assert kafka_producer.produce.call_count == 2
    assert kafka_producer.produce.call_args_list[0][0][1].event_type == RunStatusEvent.__name__
    produced_event = kafka_producer.produce.call_args_list[1][0][1]
    assert isinstance(produced_event, InstanceAlertEvent)
    assert produced_event.type == InstanceAlertType.INCOMPLETE

    assert Instance.select().where(Instance.active == True).count() == 0
    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.type == InstanceAlertType.INCOMPLETE
    assert alert.instance == instance
