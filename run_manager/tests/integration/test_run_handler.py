from datetime import datetime, timezone, UTC
from uuid import UUID

import pytest

from common.datetime_utils import timestamp_to_datetime
from common.entities import Run, RunStatus
from run_manager.context import RunManagerContext
from run_manager.event_handlers import RunHandler
from testlib.fixtures.internal_events import *


def _create_run(pipeline, status, run_key="anyrun", start_time=datetime.now()):
    return Run.create(
        key=run_key if RunStatus.has_run_started(status) else None,
        start_time=start_time if RunStatus.has_run_started(status) else None,
        pipeline=pipeline,
        status=status,
    )


@pytest.mark.integration
def test_run_handler_new_pending_metadata(run_status_event_pending, pipeline):
    handler = RunHandler(RunManagerContext(pipeline=pipeline))
    handler.handle_run_status(run_status_event_pending)

    # Retrieve the run and make sure the expected_start_time has been updated
    run = Run.get_by_id(handler.context.run.id)
    assert run.expected_start_time == datetime(2005, 3, 1, 1, 1, 1, tzinfo=UTC)


@pytest.mark.integration
def test_run_handler_no_overwrite_expected_start_time(run_status_event_missing, pipeline):
    expected_start_time = datetime(2005, 3, 2, 2, 2, 2, tzinfo=UTC)
    run = Run.create(
        id=UUID("dbed19e1-d0bb-4860-bbdf-9d768cb90764"),
        pipeline=pipeline,
        status="PENDING",
        start_time=None,
        expected_start_time=expected_start_time,
    )

    # The event expected_start_time should be different so we know we are not overwriting the existing value
    event_expected_start_time = timestamp_to_datetime(run_status_event_missing.metadata["expected_start_time"])
    assert event_expected_start_time != expected_start_time

    handler = RunHandler(RunManagerContext(pipeline=pipeline))
    handler.handle_run_status(run_status_event_missing)

    # Retrieve the run and make sure the expected_start_time has not been modified
    updated_run = Run.get_by_id(run.id)
    assert updated_run.expected_start_time == expected_start_time


@pytest.mark.integration
@pytest.mark.parametrize(
    "existing_run_status, expected",
    [
        (None, {"final_run_ct": 1, "created_run": True, "started_run": True}),
        (RunStatus.RUNNING.name, {"final_run_ct": 1, "created_run": False, "started_run": False}),
        (RunStatus.FAILED.name, {"final_run_ct": 1, "created_run": False, "started_run": False}),
        (RunStatus.PENDING.name, {"final_run_ct": 1, "created_run": False, "started_run": True}),
        (RunStatus.MISSING.name, {"final_run_ct": 2, "created_run": True, "started_run": True}),
    ],
    ids=[
        "no run create new",
        "reuse existing run",
        "existing run reached end status no action",
        "start pending run",
        "existing missing run create new",
    ],
)
def test_run_handler_context_receiving_running_run(existing_run_status, expected, pipeline, RUNNING_run_status_event):
    if existing_run_status:
        _create_run(pipeline, existing_run_status, RUNNING_run_status_event.run_key)
        context = RunManagerContext(pipeline=pipeline)
        assert Run.select().count() == 1
    else:
        context = RunManagerContext(pipeline=pipeline)
        assert Run.select().count() == 0

    handler = RunHandler(context)
    handler.handle_run_status(RUNNING_run_status_event)

    assert Run.select().count() == expected["final_run_ct"]
    assert handler.context.created_run == expected["created_run"]
    assert handler.context.started_run == expected["started_run"]


@pytest.mark.integration
def test_run_handler_context_same_pipeline_different_run_key(pipeline, run, RUNNING_run_status_event):
    assert Run.select().count() == 1

    handler = RunHandler(RunManagerContext(pipeline=pipeline))
    RUNNING_run_status_event.run_key = RUNNING_run_status_event.run_key + "2"
    handler.handle_run_status(RUNNING_run_status_event)

    assert Run.select().count() == 2
    assert handler.context.run.key == RUNNING_run_status_event.run_key
    assert handler.context.created_run is True
    assert handler.context.started_run is True


@pytest.mark.integration
@pytest.mark.parametrize(
    "existing_run_status, expected",
    [
        (None, {"final_run_ct": 1, "created_run": True, "started_run": False}),
        (RunStatus.RUNNING.name, {"final_run_ct": 2, "created_run": True, "started_run": False}),
        (RunStatus.COMPLETED.name, {"final_run_ct": 2, "created_run": True, "started_run": False}),
        (RunStatus.PENDING.name, {"final_run_ct": 1, "created_run": False, "started_run": False}),
        (RunStatus.MISSING.name, {"final_run_ct": 2, "created_run": True, "started_run": False}),
    ],
)
def test_run_handler_context_receiving_pending_run(
    existing_run_status, expected, pipeline, PENDING_run_status_event, timestamp_now
):
    if existing_run_status:
        _create_run(pipeline, existing_run_status)
        context = RunManagerContext(pipeline=pipeline)
        assert Run.select().count() == 1
    else:
        context = RunManagerContext(pipeline=pipeline)
        assert Run.select().count() == 0

    handler = RunHandler(context)
    handler.handle_run_status(PENDING_run_status_event)

    assert Run.select().count() == expected["final_run_ct"]
    assert handler.context.created_run == expected["created_run"]
    assert handler.context.started_run == expected["started_run"]


@pytest.mark.integration
def test_run_handler_context_receiving_missing_run(pipeline, pending_run, MISSING_run_status_event):
    assert Run.select().count() == 1

    handler = RunHandler(RunManagerContext(pipeline=pipeline))
    handler.handle_run_status(MISSING_run_status_event)

    assert Run.select().count() == 1
    assert handler.context.created_run is False
    assert handler.context.started_run is False


@pytest.mark.integration
@pytest.mark.parametrize("event_fixture", ["metric_log_event", "message_log_event", "test_outcomes_event"])
@pytest.mark.parametrize(
    "existing_run_status, expected",
    [
        (None, {"final_run_ct": 1, "created_run": True, "started_run": True}),
        (RunStatus.RUNNING.name, {"final_run_ct": 1, "created_run": False, "started_run": False}),
        (RunStatus.FAILED.name, {"final_run_ct": 1, "created_run": False, "started_run": False}),
        (RunStatus.PENDING.name, {"final_run_ct": 1, "created_run": False, "started_run": True}),
        (RunStatus.MISSING.name, {"final_run_ct": 2, "created_run": True, "started_run": True}),
    ],
    ids=[
        "no run create new",
        "reuse existing run",
        "do nothing on existing run that reached end status",
        "start pending run",
        "existing missing run create new",
    ],
)
def test_run_handler_context_receiving_other_event_types(
    event_fixture, existing_run_status, expected, pipeline, timestamp_now, request
):
    event = request.getfixturevalue(event_fixture)
    if existing_run_status:
        _create_run(pipeline, existing_run_status, event.run_key)
        context = RunManagerContext(pipeline=pipeline)
        assert Run.select().count() == 1
    else:
        context = RunManagerContext(pipeline=pipeline)
        assert Run.select().count() == 0

    handler = RunHandler(context)
    handler._handle_event(event)

    assert Run.select().count() == expected["final_run_ct"]
    assert handler.context.created_run == expected["created_run"]
    assert handler.context.started_run == expected["started_run"]
