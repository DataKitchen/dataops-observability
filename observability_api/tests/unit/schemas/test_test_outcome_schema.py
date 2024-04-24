import pytest
from marshmallow import ValidationError

from common.events.v1 import TestStatuses
from observability_api.schemas import TestOutcomeSummarySchema


@pytest.mark.unit
@pytest.mark.parametrize("status", [TestStatuses.PASSED.name, TestStatuses.WARNING.name, TestStatuses.FAILED.name])
def test_test_outcome_status_schema_load(status):
    data = TestOutcomeSummarySchema().load({"status": status, "count": 1})
    assert data["status"] == status


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    [
        {"status": "INVALID VALUE", "count": 1},
        {"test_status": TestStatuses.PASSED.name, "count": 1},
        {"status": None, "count": 1},
        {},
    ],
    ids=("invalid status", "unknown field", "empty status", "empty summary"),
)
def test_test_outcome_status_schema_load_invalid(data):
    with pytest.raises(ValidationError):
        TestOutcomeSummarySchema().load(data)
