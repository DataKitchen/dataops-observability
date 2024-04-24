import copy

import pytest

from common.entities import Run, RunTask, Task
from run_manager.context import RunManagerContext
from run_manager.event_handlers import TaskHandler
from testlib.fixtures.v1_events import valid_event_keys


@pytest.fixture
def run(pipeline):
    return Run.create(pipeline=pipeline, key="run key", status="RUNNING")


@pytest.mark.integration
def test_task_handler_update_task_name(task_status_event, run, pipeline):
    run_status_event1 = copy.deepcopy(task_status_event)
    run_status_event1.task_name = "Task1"
    run_status_event1.pipeline_id = pipeline.id
    run_status_event1.run_id = run.id
    run_status_event2 = copy.deepcopy(run_status_event1)
    run_status_event2.task_name = "Task2"

    handler = TaskHandler(RunManagerContext(run=run))
    handler._identify_task(run_status_event1)

    assert Task.select().count() == 1
    task = Task.select().get()
    assert task.name == "Task1"

    handler._identify_task(run_status_event2)

    assert Task.select().count() == 1  # Should have re-used the existing task
    task = Task.select().get()
    assert task.name == "Task2"  # Task name should now be updated


@pytest.mark.integration
def test_task_handler_update_task_name_none(task_status_event, run, pipeline):
    run_status_event1 = copy.deepcopy(task_status_event)
    run_status_event1.task_name = "Task1"
    run_status_event1.pipeline_id = pipeline.id
    run_status_event1.run_id = run.id
    run_status_event2 = copy.deepcopy(run_status_event1)
    run_status_event2.task_name = None

    handler = TaskHandler(RunManagerContext(run=run))
    handler._identify_task(run_status_event1)
    #
    assert Task.select().count() == 1
    task = Task.select().get()
    assert task.name == "Task1"

    handler._identify_task(run_status_event2)

    assert Task.select().count() == 1  # Should have re-used the existing task
    task = Task.select().get()
    assert task.name == "Task1"  # Task name should not revert to None


@pytest.mark.integration
def test_task_handler_no_run_task_found(run_status_event, run, pipeline):
    handler = TaskHandler(RunManagerContext(run=run))
    handler.handle_run_status(run_status_event)

    assert Task.select().count() == 0
    assert RunTask.select().count() == 0


@pytest.mark.integration
@pytest.mark.parametrize("event_key", [key for key in valid_event_keys if key != "pipeline_key"])
def test_task_handler_non_batch_pipeline_event_no_action(event_key, request, message_log_event, project):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(message_log_event)
    setattr(event, event_key, component.key)
    event.pipeline_key = None
    handler = TaskHandler(RunManagerContext(component=component))
    handler.handle_message_log(event)

    assert Task.select().count() == 0
    assert RunTask.select().count() == 0
