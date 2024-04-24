import pytest
from peewee import DoesNotExist

from common.events.base import BatchPipelineMixin, ProjectMixin, TaskMixin
from testlib.fixtures.entities import *


@pytest.mark.integration
def test_project_mixing(project):
    pm = ProjectMixin(project_id=project.id)
    assert pm.project == project
    assert pm.partition_identifier == str(project.id)


@pytest.mark.integration
def test_batch_pipeline_mixin_valid(pipeline, run):
    bm = BatchPipelineMixin(batch_pipeline_id=pipeline.id, run_id=run.id)
    assert bm.batch_pipeline == pipeline
    assert bm.run == run


@pytest.mark.integration
def test_batch_pipeline_mixin_invalid(pipeline, run):
    bm = BatchPipelineMixin(batch_pipeline_id=None, run_id=None)
    with pytest.raises(DoesNotExist):
        bm.batch_pipeline
    with pytest.raises(DoesNotExist):
        bm.run


@pytest.mark.integration
def test_task_mixing_valid(task, run_task):
    bm = TaskMixin(task_id=task.id, run_task_id=run_task.id)
    assert bm.task == task
    assert bm.run_task == run_task


@pytest.mark.integration
def test_task_mixing_invalid(task, run_task):
    bm = TaskMixin(task_id=None, run_task_id=None)
    with pytest.raises(DoesNotExist):
        bm.task == task
    with pytest.raises(DoesNotExist):
        bm.run_task == run_task
