import pytest
from marshmallow import ValidationError

from common.events.v2 import DatasetOperationType
from observability_api.schemas import DatasetOperationsSummarySchema


@pytest.mark.unit
@pytest.mark.parametrize("operation", [DatasetOperationType.READ.name, DatasetOperationType.WRITE.name])
def test_dataset_operations_summary_schema_load(operation):
    data = DatasetOperationsSummarySchema().load({"operation": operation, "count": 1})
    assert data["operation"] == operation


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    [
        {"operation": "INVALID VALUE", "count": 1},
        {"status": DatasetOperationType.WRITE.name, "count": 1},
        {"operation": None, "count": 1},
        {},
    ],
    ids=("invalid operation", "unknown field", "empty operation", "empty summary"),
)
def test_dataset_operations_summary_schema_load_invalid(data):
    with pytest.raises(ValidationError):
        DatasetOperationsSummarySchema().load(data)
