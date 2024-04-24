import copy

import pytest

from common.events.v1.event import EVENT_ATTRIBUTES
from run_manager.event_handlers.component_identifier import _get_component
from testlib.fixtures.v1_events import base_events, valid_event_keys


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
@pytest.mark.parametrize("base_event", base_events)
def test_get_component_existing(event_key, base_event, request, project):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key = None
    setattr(event, event_key, component.key)
    comp = _get_component(event)
    assert comp.id == component.id
    assert comp.key == component.key
    assert comp.type == component.type


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
@pytest.mark.parametrize("base_event", base_events)
def test_get_pipeline_new_component(event_key, base_event, request, project):
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key, event.pipeline_name = None, None
    setattr(event, event_key, "a-totally-new-key")

    assert _get_component(event) is None


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
@pytest.mark.parametrize("base_event", base_events)
def test_get_component_existing_add_name(event_key, base_event, request, project):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key, event.pipeline_name = None, None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_name, None)

    # pre-check
    assert component.name is None
    assert getattr(event, EVENT_ATTRIBUTES.get(event_key).component_name) is None

    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_name, "New name")

    comp = _get_component(event)
    assert comp.id == component.id
    assert comp.key == component.key
    assert comp.name == "New name"


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
@pytest.mark.parametrize("base_event", base_events)
def test_get_component_existing_update_name(event_key, base_event, request, project):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key, event.pipeline_name = None, None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_name, "Old name")

    comp = _get_component(event)
    assert comp.id == component.id
    assert comp.key == component.key
    assert comp.name == "Old name"
    db_component = EVENT_ATTRIBUTES.get(event_key).component_model.get_by_id(component.id)
    assert db_component.name == "Old name"

    event2 = copy.deepcopy(event)
    setattr(event2, EVENT_ATTRIBUTES.get(event_key).component_name, "New name")

    comp = _get_component(event2)
    assert comp.id == component.id
    assert comp.key == component.key
    assert comp.name == "New name"


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
@pytest.mark.parametrize("base_event", base_events)
def test_get_component_existing_do_not_blank_name(event_key, base_event, request, project):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key, event.pipeline_name = None, None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_name, "my-name")

    comp = _get_component(event)
    assert comp.id == component.id
    assert comp.key == component.key
    assert comp.name == "my-name"

    event2 = copy.deepcopy(event)
    setattr(event2, EVENT_ATTRIBUTES.get(event_key).component_name, None)

    comp = _get_component(event2)
    assert comp.id == component.id
    assert comp.key == component.key
    assert comp.name == "my-name"
    db_component = EVENT_ATTRIBUTES.get(event_key).component_model.get_by_id(component.id)
    assert db_component.name == "my-name"
