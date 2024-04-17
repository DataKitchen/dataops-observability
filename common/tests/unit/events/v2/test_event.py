from uuid import uuid4

import pytest
from marshmallow.exceptions import ValidationError

from common.events.v2 import (
    BasePayloadSchema,
    BatchPipelineDataSchema,
    ComponentDataSchema,
    DatasetDataSchema,
    EventResponseSchema,
    NewComponentDataSchema,
    ServerDataSchema,
    StreamDataSchema,
)
from common.events.v2.component_data import (
    BatchPipelineData,
    ComponentData,
    DatasetData,
    NewComponentData,
    ServerData,
    StreamData,
)


@pytest.mark.unit
def test_base_payload_schema(default_base_payload_dict):
    assert BasePayloadSchema().load({}) == default_base_payload_dict


@pytest.mark.unit
def test_batch_pipeline_data_schema():
    with pytest.raises(ValidationError, match="batch_key"):
        BatchPipelineDataSchema().load({"run_key": "value2"})
    with pytest.raises(ValidationError, match="run_key"):
        BatchPipelineDataSchema().load({"batch_key": "value1"})

    assert BatchPipelineDataSchema().load({"batch_key": "value1", "run_key": "value2"}) == BatchPipelineData(
        batch_key="value1",
        run_key="value2",
        run_name=None,
        task_key=None,
        task_name=None,
        details=None,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("component_data_schema", "key_attribute"),
    (
        (DatasetDataSchema, "dataset_key"),
        (ServerDataSchema, "server_key"),
        (StreamDataSchema, "stream_key"),
    ),
)
def test_simple_component_data(component_data_schema, key_attribute):
    key_value = "Ten full tree election."
    component_data = component_data_schema().load({key_attribute: key_value})
    assert getattr(component_data, key_attribute) == key_value
    assert component_data.details is None

    with pytest.raises(ValidationError, match=key_attribute):
        component_data_schema().load({})


@pytest.mark.unit
@pytest.mark.parametrize("data", ({}, {"dataset": {"dataset_key": "k"}, "server": {"server_key": "k"}}))
def test_component_data_schema_invalid(data):
    with pytest.raises(ValidationError, match="Exactly one"):
        ComponentDataSchema().load(data)


@pytest.mark.unit
def test_component_data_schema_valid():
    expected = ComponentData(
        batch_pipeline=BatchPipelineData(
            batch_key="value1",
            run_key="value2",
            run_name=None,
            task_key=None,
            task_name=None,
            details=None,
        ),
        dataset=None,
        server=None,
        stream=None,
    )
    assert ComponentDataSchema().load({"batch_pipeline": {"batch_key": "value1", "run_key": "value2"}}) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("component_data_class", "component_attribute", "key_attribute"),
    (
        (DatasetData, "dataset", "dataset_key"),
        (ServerData, "server", "server_key"),
        (StreamData, "stream", "stream_key"),
    ),
)
def test_component_data_schema_valid_simple_component(component_data_class, component_attribute, key_attribute):
    key_value = "Reason him interesting group."
    params = {
        "dataset": None,
        "server": None,
        "stream": None,
        "batch_pipeline": None,
    }
    params.update({component_attribute: component_data_class(**{key_attribute: key_value, "details": None})})
    expected = ComponentData(
        **params,
    )
    assert ComponentDataSchema().load({component_attribute: {key_attribute: key_value}}) == expected


@pytest.mark.unit
def test_new_component_data_schema():
    assert NewComponentDataSchema().load({}) == NewComponentData(
        name=None,
        tool=None,
    )


@pytest.mark.unit
def test_event_response_schema():
    uuid = uuid4()
    assert EventResponseSchema().dump({"event_id": uuid}) == {"event_id": str(uuid)}
