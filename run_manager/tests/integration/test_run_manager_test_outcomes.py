import copy
from uuid import uuid4

import pytest

from common.entities import Dataset, Pipeline, Run, RunTask, RunTaskStatus, Server, StreamingPipeline, Task, TestOutcome
from common.events.v1.test_outcomes_event import TestOutcomeItem
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS, KafkaMessage
from run_manager.run_manager import RunManager


def pre_check(pipeline_count: int = 0, other_component_count: int = 0):
    return (
        (
            Dataset.select().count() + Server.select().count() + StreamingPipeline.select().count()
            == other_component_count
        )
        and (Pipeline.select().count() == pipeline_count)
        and (Run.select().count() == 0)
        and (Task.select().count() == 0)
        and (TestOutcome.select().count() == 0)
    )


@pytest.mark.integration
def test_run_manager_insert_run_test_outcomes_to_nonexistent_pipeline(
    kafka_consumer, kafka_producer, test_outcomes_event, test_outcomes_message
):
    # verify that there is no existing pipeline
    # Send unidentified test outcome event
    # create new pipeline and run
    # verify test outcomes are inserted
    assert pre_check()

    kafka_consumer.__iter__.return_value = iter((test_outcomes_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 0
    assert TestOutcome.select().count() == 1
    test_outcome = TestOutcome.get()
    assert test_outcome.name == test_outcomes_event.test_outcomes[0].name
    assert test_outcome.status == test_outcomes_event.test_outcomes[0].status
    assert test_outcome.external_url == test_outcomes_event.external_url


@pytest.mark.integration
def test_run_manager_insert_task_test_outcomes_to_nonexistent_pipeline(
    kafka_consumer, kafka_producer, test_outcomes_event, test_outcomes_message
):
    # create new pipeline, run and task; then insert test outcomes
    assert pre_check()

    test_outcomes_event_copy = copy.deepcopy(test_outcomes_message)
    test_outcomes_event_copy.payload.event_id = uuid4()
    test_outcomes_event_copy.payload.task_key = "Task key"
    kafka_consumer.__iter__.return_value = iter((test_outcomes_event_copy,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    assert TestOutcome.select().count() == 1
    test_outcome = TestOutcome.get()
    assert test_outcome.name == test_outcomes_event_copy.payload.test_outcomes[0].name
    assert test_outcome.status == test_outcomes_event_copy.payload.test_outcomes[0].status
    assert test_outcome.task.key == test_outcomes_event_copy.payload.task_key
    run_task = RunTask.get()
    assert run_task.status == RunTaskStatus.RUNNING.name
    assert test_outcome.external_url == test_outcomes_event_copy.payload.external_url


@pytest.mark.integration
def test_run_manager_insert_run_test_outcomes_to_existed_pipeline(
    kafka_consumer, kafka_producer, pipeline, test_outcomes_message
):
    assert pre_check(pipeline_count=1)

    # Scenario 1: Reuse existed pipeline and create new run
    event = copy.deepcopy(test_outcomes_message)
    event.payload.event_id = uuid4()
    event.payload.pipeline_key = pipeline.key
    kafka_consumer.__iter__.return_value = iter((event,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 0
    assert TestOutcome.select().count() == 1
    test_outcome = TestOutcome.get()
    assert test_outcome.name == event.payload.test_outcomes[0].name
    assert test_outcome.status == event.payload.test_outcomes[0].status
    assert test_outcome.external_url == event.payload.external_url

    # Scenario 2: Reuse existed pipeline and run
    event2 = copy.deepcopy(event)
    event2.payload.event_id = uuid4()
    event2.payload.test_outcomes = [TestOutcomeItem(name=f"n{i}", status="FAILED") for i in range(2)]
    kafka_consumer.__iter__.return_value = iter((event2,))
    run_manager.process_events()
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    tests = TestOutcome.select()
    assert len(list(tests)) == 3
    assert all(t.external_url == event.payload.external_url for t in list(tests))


@pytest.mark.integration
def test_run_manager_insert_task_test_outcomes_to_existed_pipeline(
    kafka_consumer, kafka_producer, pipeline, test_outcomes_message
):
    assert pre_check(pipeline_count=1)

    # Scenario 1: Reuse existed pipeline and create new run
    event = copy.deepcopy(test_outcomes_message)
    event.payload.event_id = uuid4()
    event.payload.pipeline_key = pipeline.key
    event.payload.task_key = "Some task key"

    run_manager = RunManager(kafka_consumer, kafka_producer)
    kafka_consumer.__iter__.return_value = iter((event,))

    run_manager.process_events()
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    assert TestOutcome.select().count() == 1

    # Scenario 2: Reuse existed pipeline and run
    event2 = copy.deepcopy(event)
    event2.payload.event_id = uuid4()
    event2.payload.test_outcomes = [TestOutcomeItem(name=f"n{i}", status="FAILED") for i in range(2)]
    assert len(event2.payload.test_outcomes) == 2
    kafka_consumer.__iter__.return_value = iter((event2,))

    run_manager.process_events()
    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 1
    assert RunTask.select().count() == 1
    assert TestOutcome.select().count() == 3

    # Scenario 3: Reuse existed pipeline, run and task
    event3 = copy.deepcopy(event)
    event3.payload.event_id = uuid4()
    event3.payload.task_key = "Different task key"
    assert len(event3.payload.test_outcomes) == 1
    kafka_consumer.__iter__.return_value = iter((event3,))
    run_manager.process_events()

    assert Pipeline.select().count() == 1
    assert Run.select().count() == 1
    assert Task.select().count() == 2
    assert RunTask.select().count() == 2
    assert TestOutcome.select().count() == 4


@pytest.mark.integration
@pytest.mark.parametrize("event_key", ["dataset_key", "server_key", "stream_key"])
@pytest.mark.parametrize("other_component_count", [0, 1], ids=["create new component", "use existing component"])
def test_run_manager_insert_run_test_outcomes_to_nonexistent_component(
    event_key,
    other_component_count,
    project,
    kafka_consumer,
    kafka_producer,
    test_outcomes_event,
    test_outcomes_message,
    request,
):
    event = copy.deepcopy(test_outcomes_event)
    event.id = uuid4()
    event.pipeline_key = None
    if other_component_count:
        component = request.getfixturevalue(event_key[:-4])
        setattr(event, event_key, component.key)
    else:
        component = None
        setattr(event, event_key, "some key")
    assert pre_check(other_component_count=other_component_count)
    kafka_message = KafkaMessage(payload=event, topic=TOPIC_UNIDENTIFIED_EVENTS.name, partition=2, offset=1, headers={})

    kafka_consumer.__iter__.return_value = iter((kafka_message,))
    run_manager = RunManager(kafka_consumer, kafka_producer)

    run_manager.process_events()

    assert event.component_model.select().count() == 1
    assert Run.select().count() == 0
    assert Task.select().count() == 0
    assert TestOutcome.select().count() == 1
    test_outcome = TestOutcome.get()
    assert test_outcome.name == event.test_outcomes[0].name
    assert test_outcome.status == event.test_outcomes[0].status
    assert test_outcome.component.type == event.component_type.name
    assert test_outcome.external_url == event.external_url
    if other_component_count:
        assert test_outcome.component.id == component.id
    else:
        assert test_outcome.component.id is not None
