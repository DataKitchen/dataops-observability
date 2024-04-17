import pytest
from marshmallow import ValidationError

from common.events.v1 import DatasetOperationApiSchema, DatasetOperationType


@pytest.mark.unit
def test_dataset_operation_valid():
    DatasetOperationApiSchema().load(
        {
            "dataset_key": "t",
            "operation": DatasetOperationType.READ.name,
        }
    )
    DatasetOperationApiSchema().load(
        {
            "dataset_key": "test key",
            "operation": DatasetOperationType.WRITE.name,
            "path": "test path",
        }
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "dataset_operation_dict, match_value",
    (
        ({"dataset_key": "t"}, "operation"),
        (
            {
                "pipeline_key": "k",
                "run_key": "k",
                "operation": DatasetOperationType.READ.name,
            },
            "pipeline_key",
        ),
        (
            {
                "dataset_key": "test key",
                "operation": DatasetOperationType.WRITE.name,
                "path": "",
            },
            "path",
        ),
        (
            {
                "dataset_key": "test key",
                "operation": DatasetOperationType.WRITE.name,
                "path": "a" * 4097,
            },
            "path",
        ),
        (
            {
                "dataset_key": "test key",
                "operation": "INVALID OPERATION",
            },
            "operation",
        ),
    ),
)
def test_dataset_operation_invalid(dataset_operation_dict, match_value):
    with pytest.raises(ValidationError, match=match_value):
        DatasetOperationApiSchema().load(dataset_operation_dict)
