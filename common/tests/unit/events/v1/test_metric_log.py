import copy
from decimal import Decimal

import pytest
from marshmallow import ValidationError

from common.events.v1 import MetricLogEvent
from common.events.v1.event import EVENT_ATTRIBUTES
from testlib.fixtures.v1_events import valid_event_keys


@pytest.fixture
def unidentified_metric_log_data(unidentified_event_data):
    unidentified_data_copy = unidentified_event_data.copy()
    unidentified_data_copy["metric_key"] = "key"
    unidentified_data_copy["metric_value"] = 10.0
    return unidentified_data_copy


@pytest.mark.unit
@pytest.mark.parametrize("event_key", valid_event_keys)
def test_metric_log_event_request(event_key, unidentified_metric_log_data):
    event_data = copy.deepcopy(unidentified_metric_log_data)
    if event_key != "pipeline_key":
        del event_data["pipeline_key"]
    event_data[event_key] = "some key"

    event = MetricLogEvent.as_event_from_request(event_data)
    assert event.metric_value == Decimal(event_data["metric_value"])
    assert event.event_type == "MetricLogEvent"
    assert getattr(event, event_key) == "some key"
    assert event.component_type == EVENT_ATTRIBUTES.get(event_key).component_type


@pytest.mark.unit
def test_metric_log_event_as_dict(unidentified_metric_log_data):
    event = MetricLogEvent.as_event_from_request(unidentified_metric_log_data)
    data = event.as_dict()
    assert "metric_key" in data
    assert data["event_type"] == "MetricLogEvent"


@pytest.mark.unit
def test_metric_log_event_from_dict(unidentified_metric_log_data):
    event = MetricLogEvent.as_event_from_request(unidentified_metric_log_data)
    data = event.as_dict()
    event.from_dict(data)

    assert "metric_key" in data
    assert data["event_type"] == "MetricLogEvent"


@pytest.mark.unit
def test_metric_log_event(metric_log_event_data):
    # Changing dumped value to a float so that we can validate the casting when loading using `from_dict`
    metric_log_event_data["metric_value"] = 10.0
    event = MetricLogEvent.from_dict(metric_log_event_data)
    assert event.metric_value == metric_log_event_data["metric_value"]
    assert event.metric_key == metric_log_event_data["metric_key"]
    dump = event.as_dict()
    assert dump["event_type"] == "MetricLogEvent"
    assert dump["metric_value"] == "10.0"


@pytest.mark.unit
@pytest.mark.parametrize("min_length_field", ["metric_value", "metric_key"])
def test_min_length_fields_metric_log(metric_log_event_data, min_length_field):
    metric_log_event_data[min_length_field] = ""
    with pytest.raises(ValidationError):
        MetricLogEvent.from_dict(metric_log_event_data)
