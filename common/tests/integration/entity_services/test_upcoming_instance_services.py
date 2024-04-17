from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from common.entities import InstanceRule, InstanceRuleAction
from common.entity_services import UpcomingInstanceService
from common.entity_services.helpers import ListRules, UpcomingInstanceFilters
from testlib.fixtures.entities import *


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_instance_schedule(
    journey,
    instance_rule_start,
    instance_rule_end,
    current_time,
):
    start_time = current_time.replace(minute=45)
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    instance_rule_end.expression = "30 * * * *"
    instance_rule_end.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(start_range=start_time),
        project_id=journey.project_id,
    )
    assert len(upcoming_instances) == 10
    for upcoming in upcoming_instances:
        assert upcoming.journey == journey
        assert upcoming.expected_start_time is not None
        assert upcoming.expected_end_time is not None


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_only_start_times(
    company,
    journey,
    instance_rule_start,
    current_time,
):
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(start_range=current_time),
        company_id=company.id,
    )
    assert len(upcoming_instances) == 10
    for upcoming in upcoming_instances:
        assert upcoming.journey == journey
        assert upcoming.expected_start_time is not None
        assert upcoming.expected_end_time is None


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_only_end_times(
    company,
    journey,
    instance_rule_end,
    current_time,
):
    instance_rule_end.expression = "30 * * * *"
    instance_rule_end.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(start_range=current_time, project_ids=[journey.project_id]),
        company_id=company.id,
    )
    assert len(upcoming_instances) == 10
    for upcoming in upcoming_instances:
        assert upcoming.journey == journey
        assert upcoming.expected_start_time is None
        assert upcoming.expected_end_time is not None


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_with_end_time_filter(
    journey,
    instance_rule_start,
    current_time,
):
    start_time = current_time.replace(minute=45)
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(
            start_range=start_time, end_range=(start_time + timedelta(hours=7)), journey_ids=[journey.id]
        ),
        project_id=journey.project_id,
    )
    assert len(upcoming_instances) == 7
    for upcoming in upcoming_instances:
        assert upcoming.journey == journey
        assert upcoming.expected_start_time is not None
        assert upcoming.expected_end_time is None


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_mixed_set_times(
    journey,
    instance_rule_start,
    instance_rule_end,
    current_time,
):
    start_time = current_time.replace(minute=59)
    instance_rule_start.expression = "5,10,25 * * * *"
    instance_rule_start.save()
    instance_rule_end.expression = "0,15,20,30,35 * * * *"
    instance_rule_end.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(
            start_range=start_time, end_range=(start_time + timedelta(hours=1)), journey_names=[journey.name]
        ),
        project_id=journey.project_id,
    )
    assert len(upcoming_instances) == 6
    assert upcoming_instances[0].expected_start_time is None
    assert upcoming_instances[0].expected_end_time.minute == 0

    assert upcoming_instances[1].expected_start_time.minute == 5
    assert upcoming_instances[1].expected_end_time is None

    assert upcoming_instances[2].expected_start_time.minute == 10
    assert upcoming_instances[2].expected_end_time.minute == 15

    assert upcoming_instances[3].expected_start_time is None
    assert upcoming_instances[3].expected_end_time.minute == 20

    assert upcoming_instances[4].expected_start_time.minute == 25
    assert upcoming_instances[4].expected_end_time.minute == 30

    assert upcoming_instances[5].expected_start_time is None
    assert upcoming_instances[5].expected_end_time.minute == 35


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_negative_count(
    journey,
    instance_rule_start,
    current_time,
):
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(count=-1),
        UpcomingInstanceFilters(start_range=current_time),
        project_id=journey.project_id,
    )
    assert len(upcoming_instances) == 0


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_batch_schedule(
    journey,
    batch_start_schedule,
    batch_end_schedule,
    instance_rule_pipeline_start,
    instance_rule_pipeline_end,
    current_time,
):
    batch_start_schedule.expression = "0 * * * *"
    batch_start_schedule.save()
    batch_end_schedule.expression = "30 * * * *"
    batch_end_schedule.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(start_range=current_time),
        project_id=journey.project_id,
    )
    assert len(upcoming_instances) == 10
    for upcoming in upcoming_instances:
        assert upcoming.journey == journey
        assert upcoming.expected_start_time is not None
        assert upcoming.expected_end_time is not None


@pytest.mark.integration
@pytest.mark.parametrize(
    "filters",
    (
        UpcomingInstanceFilters(project_ids=[uuid4()]),
        UpcomingInstanceFilters(journey_ids=[uuid4()]),
        UpcomingInstanceFilters(journey_names=[str(uuid4())]),
    ),
)
def test_get_upcoming_instances_with_rules_filter_out_schedules(
    company,
    journey,
    instance_rule_start,
    current_time,
    filters,
):
    plain_filters = UpcomingInstanceFilters(start_range=current_time)
    filters.start_range = current_time
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        filters,
        company_id=company.id,
    )
    assert len(upcoming_instances) == 0

    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        plain_filters,
        company_id=company.id,
    )
    assert len(upcoming_instances) == 10


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_both_company_and_project_filter(
    company,
    journey,
    instance_rule_start,
    current_time,
):
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    with pytest.raises(ValueError, match="exactly one"):
        UpcomingInstanceService.get_upcoming_instances_with_rules(
            ListRules(),
            UpcomingInstanceFilters(start_range=current_time),
            project_id=journey.project_id,
            company_id=company.id,
        )


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_nothing_in_time_range(
    company,
    journey,
    instance_rule_start,
    current_time,
):
    start_time = current_time.replace(minute=10)
    instance_rule_start.expression = "0 * * * *"
    instance_rule_start.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(),
        UpcomingInstanceFilters(start_range=start_time, end_range=(start_time + timedelta(minutes=30))),
        company_id=company.id,
    )
    assert len(upcoming_instances) == 0


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_two_journeys(
    company,
    journey,
    journey_2,
    current_time,
):
    start_time = current_time.replace(minute=59)
    InstanceRule.create(journey=journey, action=InstanceRuleAction.START, expression="0 * * * *")
    InstanceRule.create(journey=journey_2, action=InstanceRuleAction.START, expression="30 * * * *")
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(count=2),
        UpcomingInstanceFilters(start_range=start_time),
        company_id=company.id,
    )
    assert len(upcoming_instances) == 2
    assert upcoming_instances[0].journey == journey
    assert upcoming_instances[0].expected_start_time is not None
    assert upcoming_instances[0].expected_end_time is None

    assert upcoming_instances[1].journey == journey_2
    assert upcoming_instances[1].expected_start_time is not None
    assert upcoming_instances[1].expected_end_time is None


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_discard_matching_existing_instance(
    company,
    journey,
    instance,
    instance_rule_end,
    current_time,
):
    base_time = datetime(2023, 8, 21, 10, 0, 0, tzinfo=timezone.utc)
    instance.start_time = base_time
    instance.save()
    instance_rule_end.expression = "30 * * * *"
    instance_rule_end.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(count=1),
        UpcomingInstanceFilters(start_range=base_time, project_ids=[journey.project_id]),
        company_id=company.id,
    )
    assert len(upcoming_instances) == 1
    assert upcoming_instances[0].expected_start_time is None
    assert upcoming_instances[0].expected_end_time != (base_time + timedelta(minutes=30))
    assert upcoming_instances[0].expected_end_time == (base_time + timedelta(minutes=90))


@pytest.mark.integration
def test_get_upcoming_instances_with_rules_do_not_discard_upcoming_instance(
    company,
    journey,
    instance,
    instance_rule_start,
    instance_rule_end,
    current_time,
):
    base_time = datetime(2023, 8, 21, 10, 0, 0, tzinfo=timezone.utc)
    instance.start_time = base_time
    instance.save()
    instance_rule_start.expression = "5 * * * *"
    instance_rule_start.save()
    instance_rule_end.expression = "30 * * * *"
    instance_rule_end.save()
    upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
        ListRules(count=1),
        UpcomingInstanceFilters(start_range=base_time, project_ids=[journey.project_id]),
        company_id=company.id,
    )
    assert len(upcoming_instances) == 1
    assert upcoming_instances[0].expected_start_time == (base_time + timedelta(minutes=5))
    assert upcoming_instances[0].expected_end_time == (base_time + timedelta(minutes=30))
