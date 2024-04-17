import copy

import pytest
from marshmallow import ValidationError

from common.events.v1 import MessageEventLogLevel, MessageLogEvent
from common.events.v1.event import EVENT_ATTRIBUTES
from testlib.fixtures.v1_events import valid_event_keys


@pytest.fixture
def unidentified_message_log_data(unidentified_event_data):
    unidentified_data_copy = unidentified_event_data.copy()
    unidentified_data_copy["log_level"] = MessageEventLogLevel.INFO.name
    unidentified_data_copy["message"] = "Test Message"
    return unidentified_data_copy


@pytest.mark.unit
@pytest.mark.parametrize("event_key", valid_event_keys)
def test_message_log_event_request(event_key, unidentified_message_log_data):
    event_data = copy.deepcopy(unidentified_message_log_data)
    if event_key != "pipeline_key":
        del event_data["pipeline_key"]
    event_data[event_key] = "some key"

    event = MessageLogEvent.as_event_from_request(event_data)
    assert event.log_level == MessageEventLogLevel.INFO.name
    assert event.message == event_data["message"]
    assert event.event_type == "MessageLogEvent"
    assert getattr(event, event_key) == "some key"
    assert event.component_type == EVENT_ATTRIBUTES.get(event_key).component_type


@pytest.mark.unit
def test_message_log_event_as_dict(unidentified_message_log_data):
    event = MessageLogEvent.as_event_from_request(unidentified_message_log_data)
    data = event.as_dict()
    assert "message" in data
    assert data["event_type"] == "MessageLogEvent"


@pytest.mark.unit
def test_message_log_event_from_dict(unidentified_message_log_data):
    event = MessageLogEvent.as_event_from_request(unidentified_message_log_data)
    data = event.as_dict()
    event.from_dict(data)

    assert "message" in data
    assert data["event_type"] == "MessageLogEvent"


@pytest.mark.unit
def test_message_log_event(message_log_event_data):
    event: MessageLogEvent = MessageLogEvent.from_dict(message_log_event_data)
    assert event.log_level == MessageEventLogLevel.INFO.name
    assert event.message == message_log_event_data["message"]
    dump = event.as_dict()
    assert dump["event_type"] == "MessageLogEvent"
    assert dump["log_level"] == MessageEventLogLevel.INFO.name
    assert dump["message"] == message_log_event_data["message"]


@pytest.mark.unit
def test_message_level_is_case_insensitive(message_log_event_data):
    message_log_event_data["log_level"] = MessageEventLogLevel.INFO.name.lower()
    event = MessageLogEvent.from_dict(message_log_event_data)
    assert event.log_level == MessageEventLogLevel.INFO.name

    message_log_event_data.pop("log_level")
    # ensure our preload handles invalid data.
    with pytest.raises(ValidationError):
        MessageLogEvent.from_dict(message_log_event_data)


@pytest.mark.unit
def test_message_log_min_length_message(message_log_event_data):
    message_log_event_data["message"] = ""
    with pytest.raises(ValidationError):
        MessageLogEvent.from_dict(message_log_event_data)


@pytest.mark.unit
def test_message_log_validate_default_values(message_log_event_data):
    message_log_event_data.pop("task_key", None)
    # Schema-validating an arbitrary dict is not the same thing as validating a
    # Event turned into a dict as the dataclass has default values that may not
    # be valid. Therefore the Event instance is validated (e.g. what happens
    # when consuming an Event)
    result = MessageLogEvent.from_dict(message_log_event_data)
    MessageLogEvent.from_dict(result.as_dict())
