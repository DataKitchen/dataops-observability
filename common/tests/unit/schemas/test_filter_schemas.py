from datetime import datetime, timedelta

import pytest
from marshmallow import ValidationError

from common.schemas.filter_schemas import FiltersSchema


@pytest.mark.unit
def test_validate_time_range_valid():
    now = datetime.now()
    later = now + timedelta(hours=5)
    FiltersSchema().validate_time_range(None, None, "N/A")
    FiltersSchema().validate_time_range(None, later, "N/A")
    FiltersSchema().validate_time_range(now, None, "N/A")
    FiltersSchema().validate_time_range(now, later, "N/A")


@pytest.mark.unit
def test_validate_time_range_invalid():
    now = datetime.now()
    earlier = now - timedelta(hours=5)

    with pytest.raises(ValidationError):
        FiltersSchema().validate_time_range(now, earlier, "N/A")
