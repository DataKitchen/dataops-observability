import pytest
from marshmallow.exceptions import ValidationError

from common.events.v2 import LogEntry, LogLevel, MessageLog
from common.events.v2.message_log import LogEntrySchema, MessageLogSchema


@pytest.fixture
def log_entry_data():
    return {"level": "INFO", "message": "Lorem ipsum"}


@pytest.fixture
def log_entry(log_entry_data):
    return LogEntry(level=LogLevel.__getitem__(log_entry_data["level"]), message=log_entry_data["message"])


@pytest.fixture
def message_log_data(component_data_dict, log_entry_data):
    return {
        "component": component_data_dict,
        "log_entries": [log_entry_data],
    }


@pytest.mark.unit
def test_log_entry_invalid():
    with pytest.raises(ValidationError, match="level"):
        LogEntrySchema().load({"message": "Lorem ipsum"})
    with pytest.raises(ValidationError, match="message"):
        LogEntrySchema().load({"level": "INFO"})
    with pytest.raises(ValidationError, match="level"):
        LogEntrySchema().load({"message": "Lorem ipsum", "level": "invalid level"})


@pytest.mark.unit
def test_log_entry(log_entry_data, log_entry):
    assert LogEntrySchema().load(log_entry_data) == log_entry


@pytest.mark.unit
def test_log_entries(default_base_payload_dict, message_log_data, log_entry, default_component_data):
    expected_result = MessageLog(
        component=default_component_data,
        log_entries=[log_entry],
        **default_base_payload_dict,
    )
    assert MessageLogSchema().load(message_log_data) == expected_result


@pytest.mark.unit
def test_message_log_empty(message_log_data):
    del message_log_data["log_entries"]
    with pytest.raises(ValidationError, match="log_entries"):
        MessageLogSchema().load(message_log_data)

    message_log_data["log_entries"] = []
    with pytest.raises(ValidationError, match="log_entries"):
        MessageLogSchema().load(message_log_data)
