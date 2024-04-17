import pytest

from common.entities import Schedule, ScheduleExpectation


@pytest.mark.integration
def test_schedule_create(pipeline):
    Schedule.create(
        component=pipeline,
        description="Some cool schedule",
        schedule="25 */2 * * *",
        timezone="EST",
        expectation=ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
        margin=120,
    )
