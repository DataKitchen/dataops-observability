from datetime import datetime

import pytest

from common.entities import Run, RunStatus
from rules_engine.rule_data import DatabaseData
from testlib.fixtures.entities import *
from testlib.fixtures.v1_events import *


@pytest.mark.integration
def test_databasedata_runs_sorting(pipeline, RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = pipeline.id
    runs = [
        Run.create(status=RunStatus.COMPLETED, key="1", pipeline=pipeline),
        Run.create(
            expected_start_time=datetime.utcnow(), start_time=None, status=RunStatus.PENDING.name, pipeline=pipeline
        ),
        Run.create(status=RunStatus.COMPLETED, key="3", pipeline=pipeline),
    ]
    runs.reverse()

    assert DatabaseData(RUNNING_run_status_event).runs.count() == 3
    for i, run in enumerate(DatabaseData(RUNNING_run_status_event).runs):
        assert run.id == runs[i].id


@pytest.mark.integration
def test_databasedata_runs_unset_pipeline_id(RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = None
    with pytest.raises(AttributeError):
        DatabaseData(RUNNING_run_status_event).runs


@pytest.mark.integration
def test_databasedata_runs_filter_name_sorting(pipeline, RUNNING_run_status_event):
    run_name = "test name"
    runs = [
        Run.create(status=RunStatus.COMPLETED, name=run_name, key="1", pipeline=pipeline),
        Run.create(
            expected_start_time=datetime.utcnow(), start_time=None, status=RunStatus.PENDING.name, pipeline=pipeline
        ),
        Run.create(status=RunStatus.COMPLETED, name=run_name, key="3", pipeline=pipeline),
    ]
    runs.reverse()
    runs = [r for r in runs if r.name is not None]
    RUNNING_run_status_event.pipeline_id = pipeline.id
    RUNNING_run_status_event.run_id = runs[0].id

    assert DatabaseData(RUNNING_run_status_event).runs_filter_name.count() == 2
    for i, run in enumerate(DatabaseData(RUNNING_run_status_event).runs_filter_name):
        assert run.id == runs[i].id
