import pytest
from marshmallow.exceptions import ValidationError

from common.events.v2 import MetricEntry, MetricLog
from common.events.v2.metric_log import MetricEntrySchema, MetricLogSchema


@pytest.fixture
def metric_entry_data():
    return {"key": "row_count", "value": 100}


@pytest.fixture
def metric_entry(metric_entry_data):
    return MetricEntry(**metric_entry_data)


@pytest.fixture
def metric_log_data(component_data_dict, metric_entry_data):
    return {
        "component": component_data_dict,
        "metric_entries": [metric_entry_data],
    }


@pytest.mark.unit
def test_metric_entry_invalid():
    with pytest.raises(ValidationError, match="key"):
        MetricEntrySchema().load({"value": 100})
    with pytest.raises(ValidationError, match="value"):
        MetricEntrySchema().load({"key": "row_count"})


@pytest.mark.unit
def test_metric_entry(metric_entry_data, metric_entry):
    assert MetricEntrySchema().load(metric_entry_data) == metric_entry


@pytest.mark.unit
def test_metric_entries(default_base_payload_dict, metric_log_data, metric_entry, default_component_data):
    expected_result = MetricLog(
        component=default_component_data,
        metric_entries=[metric_entry],
        **default_base_payload_dict,
    )
    assert MetricLogSchema().load(metric_log_data) == expected_result


@pytest.mark.unit
def test_metric_log_empty(metric_log_data):
    del metric_log_data["metric_entries"]
    with pytest.raises(ValidationError, match="metric_entries"):
        MetricLogSchema().load(metric_log_data)

    metric_log_data["metric_entries"] = []
    with pytest.raises(ValidationError, match="metric_entries"):
        MetricLogSchema().load(metric_log_data)
