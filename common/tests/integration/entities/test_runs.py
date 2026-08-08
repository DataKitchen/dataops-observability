from datetime import datetime, timedelta, timezone, UTC

import pytest
from peewee import IntegrityError

from common.entities import Run, RunStatus


@pytest.mark.integration
def test_add_pipeline_run_disallow_duplicate_run_key(pipeline):
    """
    Duplicate run keys are not allowed
    """
    Run.create(key="mykey", pipeline=pipeline, status=RunStatus.RUNNING.name)
    with pytest.raises(IntegrityError):
        Run.create(key="mykey", pipeline=pipeline, status=RunStatus.RUNNING.name)


@pytest.mark.integration
def test_run_status_required(pipeline):
    Run.create(key="mykey", pipeline=pipeline, status=RunStatus.RUNNING.name)
    with pytest.raises(IntegrityError):
        Run.create(key="mykey", pipeline=pipeline)


@pytest.mark.integration
def test_add_pipeline_run_listening(pipeline):
    run = Run.create(key="mykey", status="RUNNING", name="eye", pipeline=pipeline)
    run.save()

    # After adding non-RUNNING status, listening should be False
    run.end_time = datetime.utcnow().replace(tzinfo=UTC) + timedelta(days=3)
    run.status = "COMPLETED"
    run.save()

    # Make sure comparing datetime values works and start_time is a valid alias for created_on
    assert run.start_time < run.end_time


@pytest.mark.integration
def test_add_pipeline_run_start_end(pipeline):
    run = Run.create(key="mykey", pipeline=pipeline, status=RunStatus.RUNNING.name)
    run.end_time = datetime(1861, 10, 20, 10, 10, 10)
    run.save()  # end_time can be before created_on (start_time)


@pytest.mark.integration
def test_null_key(pipeline):
    Run.create(key=None, start_time=None, pipeline=pipeline, status=RunStatus.PENDING.name)
    Run.create(key=None, start_time=None, pipeline=pipeline, status=RunStatus.MISSING.name)
    Run.create(key="key", start_time=datetime.now(), pipeline=pipeline, status=RunStatus.RUNNING.name)
    with pytest.raises(IntegrityError):
        Run.create(key="key", start_time=None, pipeline=pipeline, status=RunStatus.PENDING.name)
    with pytest.raises(IntegrityError):
        Run.create(key="key", start_time=None, pipeline=pipeline, status=RunStatus.MISSING.name)
    with pytest.raises(IntegrityError):
        Run.create(key=None, start_time=datetime.now(), pipeline=pipeline, status=RunStatus.RUNNING.name)


@pytest.mark.integration
def test_null_start_time(pipeline):
    Run.create(start_time=None, key=None, pipeline=pipeline, status=RunStatus.PENDING.name)
    Run.create(start_time=None, key=None, pipeline=pipeline, status=RunStatus.MISSING.name)
    Run.create(start_time=datetime.now(), key="k3", pipeline=pipeline, status=RunStatus.RUNNING.name)
    with pytest.raises(IntegrityError):
        Run.create(start_time=datetime.now(), key=None, pipeline=pipeline, status=RunStatus.PENDING.name)
    with pytest.raises(IntegrityError):
        Run.create(start_time=datetime.now(), key=None, pipeline=pipeline, status=RunStatus.MISSING.name)
    with pytest.raises(IntegrityError):
        Run.create(start_time=None, key="k4", pipeline=pipeline, status=RunStatus.RUNNING.name)
