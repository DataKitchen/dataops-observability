from datetime import datetime

import pytest
from peewee import IntegrityError

from common.entities import Pipeline, Run, RunStatus, RunTask, RunTaskStatus, Task


@pytest.mark.integration
def test_task_no_dupliate_task_key(pipeline):
    Task.create(key="test task", pipeline=pipeline)
    with pytest.raises(IntegrityError):
        Task.create(key="test task", pipeline=pipeline)


@pytest.mark.integration
def test_task_same_name_different_pipelines(project, pipeline):
    pipeline2 = Pipeline.create(key="fake pipeline2", project=project)
    Task.create(key="test task", pipeline=pipeline)
    Task.create(key="test task", pipeline=pipeline2)


@pytest.mark.integration
def test_runtask_defaults(pipeline, pipeline_run):
    task = Task.create(key="test task", pipeline=pipeline)
    run_task = RunTask.create(run=pipeline_run, task=task)
    assert run_task.status == RunTaskStatus.PENDING.name
    assert run_task.end_time is None


@pytest.mark.integration
def test_add_runtask_no_duplicate_task_run(pipeline, pipeline_run):
    task = Task.create(key="Fake Task", pipeline=pipeline)
    RunTask.create(run=pipeline_run, task=task)
    with pytest.raises(IntegrityError):
        RunTask.create(run=pipeline_run, task=task)


@pytest.mark.integration
def test_add_runtask_same_task_different_run(pipeline, pipeline_run):
    pipeline_run2 = Run.create(key="fake key", pipeline=pipeline, status=RunStatus.RUNNING.name)
    task = Task.create(key="Fake Task", pipeline=pipeline)
    RunTask.create(run=pipeline_run, task=task)
    RunTask.create(run=pipeline_run2, task=task)


@pytest.mark.integration
def test_add_runtask_same_run_different_task(pipeline, pipeline_run):
    task1 = Task.create(key="Fake Task1", pipeline=pipeline)
    task2 = Task.create(key="Fake Task2", pipeline=pipeline)
    RunTask.create(run=pipeline_run, task=task1)
    RunTask.create(run=pipeline_run, task=task2)


@pytest.mark.integration
def test_run_task_end_time_before_start_time(pipeline, pipeline_run):
    # The user provides the timestamps so we can't make constraints on them
    task = Task.create(key="test task", pipeline=pipeline)
    run_task = RunTask.create(run=pipeline_run, task=task)
    run_task.end_time = datetime(1861, 10, 20, 10, 10, 10)
    run_task.save()


@pytest.mark.integration
def test_task_display_name(pipeline):
    task = Task.create(key="test task", name="Awesome Task", pipeline=pipeline)
    assert "Awesome Task" == task.display_name


@pytest.mark.integration
def test_task_display_name_fallback(pipeline):
    """Task display_name attribute falls back to task key if name not set."""
    task = Task.create(key="c24385b1-2169-4c39-8768-e7c589b1d8bd", pipeline=pipeline)
    assert "c24385b1-2169-4c39-8768-e7c589b1d8bd" == task.display_name
