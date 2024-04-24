import pytest

from common.events.v1 import MessageEventLogLevel, MessageLogEvent


@pytest.mark.integration
@pytest.mark.parametrize("component_type", ("pipeline", "dataset", "server", "stream"))
def test_get_component(component_type, unidentified_event_data_no_keys, request):
    unidentified_event_data_no_keys["message"] = "lorem ipsum"
    unidentified_event_data_no_keys["log_level"] = MessageEventLogLevel.INFO.name
    unidentified_event_data_no_keys[f"{component_type}_key"] = "some key"
    unidentified_event_data_no_keys["run_key"] = "RK" if component_type == "pipeline" else None
    component = request.getfixturevalue(component_type)
    event = MessageLogEvent.as_event_from_request(unidentified_event_data_no_keys)
    event.component_id = component.id

    assert event.component == component
    assert type(event.component) == type(component)
