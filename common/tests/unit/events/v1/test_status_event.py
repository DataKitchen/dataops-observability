import pytest
from marshmallow import ValidationError

from common.constants.validation_messages import RUNSTATUS_EVENT_MISSING_REQUIRED_KEY
from common.events.v1 import ApiRunStatus, RunStatusEvent


@pytest.fixture
def unidentified_status_data(unidentified_event_data):
    unidentified_data_copy = unidentified_event_data.copy()
    unidentified_data_copy["task_key"] = "Foo"
    unidentified_data_copy["status"] = ApiRunStatus.FAILED.name
    return unidentified_data_copy


@pytest.mark.unit
@pytest.mark.parametrize("valid_status", [e.value for e in ApiRunStatus])
def test_status_event(FAILED_run_status_event_data, valid_status):
    FAILED_run_status_event_data.update({"status": valid_status})
    status = RunStatusEvent.from_dict(FAILED_run_status_event_data)
    assert status.status == valid_status


@pytest.mark.unit
def test_status_insensitive(FAILED_run_status_event_data):
    FAILED_run_status_event_data["status"] = ApiRunStatus.FAILED.name.lower()
    result = RunStatusEvent.from_dict(FAILED_run_status_event_data)
    assert result.status == ApiRunStatus.FAILED.name

    FAILED_run_status_event_data.pop("status")
    with pytest.raises(ValidationError):
        RunStatusEvent.from_dict(FAILED_run_status_event_data)


@pytest.mark.unit
@pytest.mark.parametrize("missing_field_name", ("status",))
def test_status_missing_fields(FAILED_run_status_event_data, missing_field_name):
    FAILED_run_status_event_data.pop(missing_field_name)
    with pytest.raises(ValidationError):
        RunStatusEvent.from_dict(FAILED_run_status_event_data)


@pytest.mark.unit
def test_status_model_invalid_status(FAILED_run_status_event_data):
    FAILED_run_status_event_data.update({"status": "Unknown_status_enum"})
    with pytest.raises(ValidationError):
        RunStatusEvent.from_dict(FAILED_run_status_event_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    "event_key",
    [
        {"pipeline_key": "pipe-key", "run_key": None},
        {"pipeline_key": None, "run_key": "run-key"},
        {"dataset_key": "Foo", "pipeline_key": None, "run_key": None},
    ],
    ids=["missing pipeline key", "missing run key", "valid, non-pipeline key provided"],
)
def test_invalid_status_event_request(event_key, unidentified_event_data_no_keys):
    unidentified_event_data_no_keys["status"] = ApiRunStatus.FAILED.name
    unidentified_event_data_no_keys.update(event_key)
    with pytest.raises(ValidationError, match=RUNSTATUS_EVENT_MISSING_REQUIRED_KEY):
        RunStatusEvent.as_event_from_request(unidentified_event_data_no_keys)


@pytest.mark.unit
def test_status_event_request(unidentified_status_data):
    event = RunStatusEvent.as_event_from_request(unidentified_status_data)
    assert event.status == ApiRunStatus.FAILED.name
    assert event.event_type == "RunStatusEvent"


@pytest.mark.unit
def test_status_event_as_dict(unidentified_status_data):
    event = RunStatusEvent.as_event_from_request(unidentified_status_data)
    data = event.as_dict()
    assert "status" in data
    assert data["event_type"] == "RunStatusEvent"


@pytest.mark.unit
def test_status_event_from_dict(unidentified_status_data):
    event = RunStatusEvent.as_event_from_request(unidentified_status_data)
    data = event.as_dict()
    event.from_dict(data)

    assert "status" in data
    assert data["event_type"] == "RunStatusEvent"
