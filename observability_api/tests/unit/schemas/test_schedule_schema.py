import zoneinfo
from uuid import uuid4

import pytest
from marshmallow import ValidationError

from common.entities import Pipeline, Schedule, ScheduleExpectation, User
from observability_api.schemas import ScheduleSchema


@pytest.fixture
def valid_schedule_data():
    return {
        "schedule": "* 10 1-2 * *",
        "timezone": "America/Sao_Paulo",
        "expectation": ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
        "margin": 900,
        "description": "A cool Schedule",
    }


@pytest.fixture
def schedule_obj(valid_schedule_data):
    pipeline = Pipeline(id=uuid4())
    user = User(name="ScheduleUser", id=uuid4())
    return Schedule(id=uuid4(), component=pipeline, created_by=user, **valid_schedule_data)


@pytest.mark.unit
def test_schedule_schema_load(valid_schedule_data):
    schedule = ScheduleSchema().load(valid_schedule_data)
    assert schedule.timezone == zoneinfo.ZoneInfo(valid_schedule_data["timezone"])
    assert schedule.description == valid_schedule_data["description"]
    assert schedule.schedule == valid_schedule_data["schedule"]
    assert schedule.expectation == valid_schedule_data["expectation"]
    assert schedule.margin == valid_schedule_data["margin"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "expectation",
    [(ScheduleExpectation.BATCH_PIPELINE_END_TIME.value)],
)
def test_schedule_schema_validation_types_without_margin(valid_schedule_data, expectation):
    """
    Tests a ValidationError is raised when 'margin' is set for a expectation that forbids it.
    Also validates sucessful creation with a margin=None
    """
    valid_schedule_data["expectation"] = expectation

    with pytest.raises(ValidationError, match="margin"):
        ScheduleSchema().load(valid_schedule_data)

    # test sending margin=None
    valid_schedule_data["margin"] = None
    schedule = ScheduleSchema().load(valid_schedule_data)
    assert schedule.expectation == valid_schedule_data["expectation"]

    # test not sending margin
    valid_schedule_data.pop("margin")
    schedule = ScheduleSchema().load(valid_schedule_data)
    assert schedule.expectation == valid_schedule_data["expectation"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "expectation",
    [(ScheduleExpectation.BATCH_PIPELINE_START_TIME.value), (ScheduleExpectation.DATASET_ARRIVAL.value)],
)
def test_schedule_schema_validation_types_with_margin(valid_schedule_data, expectation):
    """Tests a ValidationError is raised when 'margin' is not set for a expectation that requires it."""
    valid_schedule_data["expectation"] = expectation

    # test sending margin=0
    valid_schedule_data["margin"] = 0
    with pytest.raises(ValidationError, match="margin"):
        ScheduleSchema().load(valid_schedule_data)

    # test sending margin=None
    valid_schedule_data["margin"] = None
    with pytest.raises(ValidationError, match="margin"):
        ScheduleSchema().load(valid_schedule_data)

    # test not sending margin
    valid_schedule_data.pop("margin")
    with pytest.raises(ValidationError, match="margin"):
        ScheduleSchema().load(valid_schedule_data)


@pytest.mark.unit
def test_schedule_schema_defaults(valid_schedule_data):
    valid_schedule_data.pop("timezone")
    schedule = ScheduleSchema().load(valid_schedule_data)
    assert schedule.timezone == zoneinfo.ZoneInfo("UTC")


@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_data, matching",
    [
        (
            {
                "schedule": "* * * * *",
                "expectation": ScheduleExpectation.BATCH_PIPELINE_START_TIME.name,
            },
            "margin",
        ),
        (
            {
                "schedule": "* * * * *",
                "expectation": ScheduleExpectation.BATCH_PIPELINE_START_TIME.name,
                "margin": 901,
            },
            "margin",
        ),
        (
            {
                "schedule": "* * * * *",
                "timezone": "A",
                "expectation": ScheduleExpectation.BATCH_PIPELINE_END_TIME.name,
            },
            "timezone",
        ),
        (
            {
                "schedule": "D",
                "expectation": ScheduleExpectation.BATCH_PIPELINE_END_TIME.name,
            },
            "schedule",
        ),
        (
            {
                "expectation": ScheduleExpectation.BATCH_PIPELINE_END_TIME.name,
            },
            "schedule",
        ),
    ],
)
def test_schedule_schema_load_invalid(invalid_data, matching):
    with pytest.raises(ValidationError, match=matching):
        ScheduleSchema().load(invalid_data)


@pytest.mark.unit
def test_schedule_schema_dump(valid_schedule_data, schedule_obj):
    schedule_data = ScheduleSchema().dump(schedule_obj)
    assert schedule_data["timezone"] == valid_schedule_data["timezone"]
    assert schedule_data["description"] == valid_schedule_data["description"]
    assert schedule_data["schedule"] == valid_schedule_data["schedule"]
    assert schedule_data["expectation"] == valid_schedule_data["expectation"]
    assert schedule_data["id"] == str(schedule_obj.id)
    assert schedule_data["component"] == str(schedule_obj.component.id)
    assert schedule_data["created_on"] == schedule_obj.created_on.isoformat()
    assert schedule_data["created_by"]["id"] == str(schedule_obj.created_by.id)
