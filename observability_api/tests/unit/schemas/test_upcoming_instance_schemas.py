from datetime import datetime
from uuid import uuid4

import pytest

from observability_api.schemas import UpcomingInstanceSchema


@pytest.mark.unit
def test_upcoming_instance_schema_dump():
    project_data = {"id": uuid4(), "name": "project name"}
    journey_data = {"id": uuid4(), "name": "journey name", "project": project_data}
    data = UpcomingInstanceSchema().dump(
        {
            "project": project_data,
            "journey": journey_data,
            "expected_start_time": datetime.now(),
            "expected_end_time": datetime.now(),
        }
    )
    assert data["project"]["id"] == str(project_data["id"])
    assert data["project"]["name"] == project_data["name"]
    assert data["journey"]["id"] == str(journey_data["id"])
    assert data["journey"]["name"] == journey_data["name"]
    assert isinstance(data["expected_start_time"], str)
    assert isinstance(data["expected_end_time"], str)
