import pytest
from marshmallow.exceptions import ValidationError

from common.events.v2 import DatasetOperation, DatasetOperationSchema, DatasetOperationType


@pytest.mark.unit
def test_dataset_operation_invalid(dataset_dict):
    with pytest.raises(ValidationError, match="operation"):
        DatasetOperationSchema().load({"dataset_component": dataset_dict})

    with pytest.raises(ValidationError, match="Must be one of"):
        DatasetOperationSchema().load({"operation": "INVALID TYPE", "dataset_component": dataset_dict})

    with pytest.raises(ValidationError, match="path"):
        DatasetOperationSchema().load(
            {"operation": DatasetOperationType.READ.name, "dataset_component": dataset_dict, "path": ""}
        )

    with pytest.raises(ValidationError, match="path"):
        DatasetOperationSchema().load(
            {"operation": DatasetOperationType.READ.name, "dataset_component": dataset_dict, "path": "a" * 4097}
        )


@pytest.mark.unit
def test_dataset_operation_valid(default_dataset_data, dataset_dict, default_base_payload_dict):
    expected = DatasetOperation(
        operation=DatasetOperationType.READ,
        path="some/file",
        dataset_component=default_dataset_data,
        **default_base_payload_dict,
    )
    assert (
        DatasetOperationSchema().load(
            {"operation": DatasetOperationType.READ.name, "dataset_component": dataset_dict, "path": "some/file"}
        )
        == expected
    )
