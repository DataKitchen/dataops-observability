import pytest

from common.events.v1 import ApiRunStatus, RunStatusEvent


@pytest.fixture
def close_run_event_data(unidentified_event_data):
    data = unidentified_event_data.copy()
    data["status"] = ApiRunStatus.COMPLETED.name
    return data


@pytest.fixture
def not_close_run_event_data(unidentified_event_data):
    data = unidentified_event_data.copy()
    data["status"] = ApiRunStatus.RUNNING.name
    return data


@pytest.mark.unit
def test_close_run_event_request(close_run_event_data):
    event = RunStatusEvent.as_event_from_request(close_run_event_data)
    assert event.is_close_run
    assert event.event_type == "RunStatusEvent"


@pytest.mark.unit
def test_close_run_event_as_dict(close_run_event_data):
    event = RunStatusEvent.as_event_from_request(close_run_event_data)
    data = event.as_dict()
    assert event.is_close_run
    assert data["event_type"] == "RunStatusEvent"


@pytest.mark.unit
def test_close_run_event_from_dict(close_run_event_data):
    event = RunStatusEvent.as_event_from_request(close_run_event_data)
    data = event.as_dict()
    event.from_dict(data)
    assert event.is_close_run
    assert data["status"] == ApiRunStatus.COMPLETED.name
    assert data["event_type"] == "RunStatusEvent"


@pytest.mark.unit
def test_close_run_event(COMPLETED_run_status_event_data):
    event = RunStatusEvent.from_dict(COMPLETED_run_status_event_data)
    dump = event.as_dict()
    assert dump["event_type"] == "RunStatusEvent"
    assert dump["metadata"]["key"] == COMPLETED_run_status_event_data["metadata"]["key"]


@pytest.mark.unit
def test_not_is_close_run(not_close_run_event_data):
    event = RunStatusEvent.as_event_from_request(not_close_run_event_data)
    assert event.is_close_run is False
