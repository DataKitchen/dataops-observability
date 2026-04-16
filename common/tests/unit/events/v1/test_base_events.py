import uuid
from datetime import timedelta, timezone, UTC

import pytest
from marshmallow import ValidationError

from common.constants.validation_messages import MISSING_COMPONENT_KEY, PIPELINE_EVENT_MISSING_REQUIRED_KEY
from common.entities import ComponentType, Pipeline, RunStatus
from common.events.v1 import ApiRunStatus, Event, MessageEventLogLevel, MessageLogEvent, RunStatusEvent
from common.events.v1.event import EventComponentDetails


@pytest.fixture
def valid_event_data(unidentified_event_data):
    """We need to invoke some kind of event."""
    data_copy = unidentified_event_data.copy()
    data_copy["status"] = ApiRunStatus.RUNNING.name
    return data_copy


@pytest.mark.unit
def test_valid_run_status_event(valid_event_data):
    event = RunStatusEvent.as_event_from_request(valid_event_data)
    assert event.event_id is not None
    assert event.pipeline_key == valid_event_data["pipeline_key"]
    for key in ["dataset_key", "server_key", "stream_key"]:
        assert getattr(event, key) is None
    assert event.component_type == ComponentType.BATCH_PIPELINE
    assert event.payload_keys == []


@pytest.mark.unit
@pytest.mark.parametrize(
    "component_id_field, component_key_field, component_type",
    [
        ("pipeline_id", "pipeline_key", ComponentType.BATCH_PIPELINE),
        ("dataset_id", "dataset_key", ComponentType.DATASET),
        ("server_id", "server_key", ComponentType.SERVER),
        ("stream_id", "stream_key", ComponentType.STREAMING_PIPELINE),
    ],
)
def test_valid_event_with_non_batch_pipeline_components(
    component_id_field, component_key_field, component_type, unidentified_event_data_no_keys
):
    unidentified_event_data_no_keys["message"] = "lorem ipsum"
    unidentified_event_data_no_keys["log_level"] = MessageEventLogLevel.INFO.name
    unidentified_event_data_no_keys[component_key_field] = "some key"
    unidentified_event_data_no_keys["run_key"] = "RK" if component_type is ComponentType.BATCH_PIPELINE else None
    event = MessageLogEvent.as_event_from_request(unidentified_event_data_no_keys)
    component_id = uuid.uuid4()
    setattr(event, component_id_field, component_id)

    assert event.event_id is not None
    assert getattr(event, component_key_field) == unidentified_event_data_no_keys[component_key_field]
    assert getattr(event, component_id_field) == component_id
    assert event.component_id == component_id
    assert event.component_key == "some key"
    assert event.component_type == component_type
    assert event.payload_keys == []


@pytest.mark.unit
@pytest.mark.parametrize(
    "component_id_field, component_key_field, component_type",
    [
        ("pipeline_id", "pipeline_key", ComponentType.BATCH_PIPELINE),
        ("dataset_id", "dataset_key", ComponentType.DATASET),
        ("server_id", "server_key", ComponentType.SERVER),
        ("stream_id", "stream_key", ComponentType.STREAMING_PIPELINE),
    ],
)
def test_set_component_id(component_id_field, component_key_field, component_type, unidentified_event_data_no_keys):
    unidentified_event_data_no_keys["message"] = "lorem ipsum"
    unidentified_event_data_no_keys["log_level"] = MessageEventLogLevel.INFO.name
    unidentified_event_data_no_keys[component_key_field] = "some key"
    unidentified_event_data_no_keys["run_key"] = "RK" if component_type is ComponentType.BATCH_PIPELINE else None
    event = MessageLogEvent.as_event_from_request(unidentified_event_data_no_keys)
    component_id = uuid.uuid4()

    event.component_id = component_id

    assert getattr(event, component_id_field) == component_id
    assert event.component_id == component_id


@pytest.mark.unit
def test_event_missing_required_attr(event_data):
    # If an event doesn't have any valid component key, ValueError should be raised.
    # Theoretically, this case should never happen in production because event schema enforce
    # an event data to have at least one valid component key
    event_data.update({"event_type": RunStatusEvent.__name__, "pipeline_key": None})
    event = Event(**event_data)
    with pytest.raises(ValueError, match="Event component key details cannot be parsed."):
        getattr(event, "component_key_details")
    setattr(event, "component_key_details", EventComponentDetails(ComponentType.BATCH_PIPELINE, "pipeline", Pipeline))
    with pytest.raises(ValueError, match="Component key cannot be empty."):
        getattr(event, "component_key")


@pytest.mark.unit
def test_event_with_missing_component_key_error(unidentified_event_data_no_keys):
    unidentified_event_data_no_keys["status"] = RunStatus.RUNNING.name
    for key in ["pipeline_key", "dataset_key", "server_key", "stream_key"]:
        assert getattr(unidentified_event_data_no_keys, key, None) is None
    with pytest.raises(ValidationError, match=MISSING_COMPONENT_KEY):
        RunStatusEvent.as_event_from_request(unidentified_event_data_no_keys)


@pytest.mark.unit
def test_event_with_multiple_component_keys_error(unidentified_event_data):
    unidentified_event_data["status"] = RunStatus.RUNNING.name
    unidentified_event_data["pipeline_key"] = "pipeline key"
    unidentified_event_data["dataset_key"] = "dataset key"
    with pytest.raises(ValidationError, match="pipeline_key and dataset_key cannot be set at the same time"):
        RunStatusEvent.as_event_from_request(unidentified_event_data)


@pytest.mark.unit
def test_event_with_batch_pipeline_component_missing_run_key_error(valid_event_data):
    # If pipeline_key is defined then run_key must be defined
    valid_event_data.update({"pipeline_key": "pipe", "run_key": None})
    with pytest.raises(ValidationError, match=PIPELINE_EVENT_MISSING_REQUIRED_KEY):
        RunStatusEvent.as_event_from_request(valid_event_data)


@pytest.mark.unit
@pytest.mark.parametrize(
    ["timestamp", "tz"],
    [
        ("2018-07-25T00:00:00Z", UTC),
        ("2018-07-25T00:00:00", UTC),
        ("2014-12-22T03:12:58.019077+06:00", timezone(timedelta(hours=6))),
    ],
    ids=["ZuluTime", "Naive", "TZ offset"],
)
def test_timestamp_deserialize_event(valid_event_data, timestamp, tz):
    valid_event_data["event_timestamp"] = timestamp
    event = RunStatusEvent.as_event_from_request(valid_event_data)
    assert event.event_timestamp.tzinfo == tz
