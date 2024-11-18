__all__ = ["UpcomingInstanceService"]

from dataclasses import dataclass, field
from datetime import datetime
from heapq import merge
from operator import itemgetter
from typing import Optional, cast
from collections.abc import Generator
from uuid import UUID
from zoneinfo import ZoneInfo

from common.apscheduler_extensions import get_crontab_trigger_times
from common.entities import (
    Company,
    Component,
    Instance,
    InstanceRule,
    InstanceRuleAction,
    Journey,
    Organization,
    Project,
    Schedule,
    ScheduleExpectation,
    UpcomingInstance,
)

from .helpers import ListRules, UpcomingInstanceFilters


@dataclass
class Crontab:
    crontab: str
    timezone: ZoneInfo


@dataclass
class JourneySchedules:
    start_schedules: list[Crontab] = field(default_factory=list)
    end_schedules: list[Crontab] = field(default_factory=list)


def _collect_journey_schedules(
    journey: Journey,
) -> JourneySchedules:
    schedules = JourneySchedules()
    for rule in journey.instance_rules:
        if rule.action is InstanceRuleAction.START:
            if rule.expression:
                schedules.start_schedules.append(Crontab(rule.expression, rule.timezone))
            else:
                for schedule in rule.batch_pipeline.schedules:
                    if schedule.expectation == ScheduleExpectation.BATCH_PIPELINE_START_TIME.name:
                        schedules.start_schedules.append(Crontab(schedule.schedule, schedule.timezone))
        elif rule.action == InstanceRuleAction.END:
            if rule.expression:
                schedules.end_schedules.append(Crontab(rule.expression, rule.timezone))
            else:
                for schedule in rule.batch_pipeline.schedules:
                    if schedule.expectation == ScheduleExpectation.BATCH_PIPELINE_END_TIME.name:
                        schedules.end_schedules.append(Crontab(schedule.schedule, schedule.timezone))

    return schedules


def _get_instance_times(
    schedules: JourneySchedules,
    start_time: datetime,
    end_time: Optional[datetime],
) -> Generator[tuple[datetime, bool], None, None]:
    """
    Generate a sequence of expected instance start and end times from the given schedules

    Since the schedules generate ordered times, the different schedule times can be merged to a single ordered sequence
    where expected start and end times can be paired together.
    """
    times = []
    for schedule in schedules.start_schedules:
        times.append(
            map(
                lambda t: (t, True),
                get_crontab_trigger_times(schedule.crontab, schedule.timezone, start_time, end_time),
            )
        )
    for schedule in schedules.end_schedules:
        times.append(
            map(
                lambda t: (t, False),
                get_crontab_trigger_times(schedule.crontab, schedule.timezone, start_time, end_time),
            )
        )
    yield from merge(*times, key=itemgetter(0))


class UpcomingInstanceService:
    @staticmethod
    def get_upcoming_instances_with_rules(
        rules: ListRules,
        filters: UpcomingInstanceFilters,
        project_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
    ) -> list[UpcomingInstance]:
        assert filters.start_range is not None
        memberships = []
        if bool(project_id) == bool(company_id):
            raise ValueError(f"Must set exactly one of {project_id=} and {company_id=}")
        if project_id:
            memberships.append(Project.id == project_id)
        else:
            memberships.append(Company.id == company_id)
            if filters.project_ids:
                memberships.append(Project.id.in_(filters.project_ids))
        if filters.journey_ids:
            memberships.append(Journey.id.in_(filters.journey_ids))
        if filters.journey_names:
            memberships.append(Journey.name.in_(filters.journey_names))

        query = Journey.select(Journey, Project).join(Project).join(Organization).join(Company).where(*memberships)
        journeys = query.prefetch(
            InstanceRule, Component, Schedule, Instance.select().order_by(Instance.start_time.desc()).limit(1)
        )

        upcoming_instance_generators = []
        active_instance_end = {}
        for journey in journeys:
            schedules = _collect_journey_schedules(journey)
            if schedules.end_schedules and (instance := next(iter(journey.instances), None)) and instance.active:
                # Store the active instance's expected endtime to be compared with the generated upcoming instances below
                active_instance_end[journey] = next(
                    UpcomingInstanceService.get_upcoming_instances(
                        journey, start_time=instance.start_time, schedules=schedules
                    )
                ).expected_end_time
            upcoming_instance_generators.append(
                UpcomingInstanceService.get_upcoming_instances(
                    journey, start_time=filters.start_range, end_time=filters.end_range, schedules=schedules
                )
            )

        count = rules.count
        upcoming_instances: list[UpcomingInstance] = []
        for upcoming in merge(
            *upcoming_instance_generators,
            # Casting to datetime because we know at least one of the attributes is set even thought the types
            # are Optional[datetime]
            key=lambda u: cast(datetime, (u.expected_start_time or u.expected_end_time)),
        ):
            if len(upcoming_instances) >= count:
                break
            elif (
                not upcoming.expected_start_time
                and active_instance_end.get(upcoming.journey) == upcoming.expected_end_time
            ):
                # Skip upcoming instances that is actually an existing active instance's end
                continue
            upcoming_instances.append(upcoming)
        return upcoming_instances

    @staticmethod
    def get_upcoming_instances(
        journey: Journey,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        schedules: Optional[JourneySchedules] = None,
    ) -> Generator[UpcomingInstance, None, None]:
        """
        Get upcoming instances for the given journey

        If the schedules are not provided, make sure that they are prefetched for the journey.
        """
        if schedules is None:
            schedules = _collect_journey_schedules(journey)
        current = UpcomingInstance(journey=journey)
        for time, is_start in _get_instance_times(schedules, start_time, end_time):
            if is_start:
                if current.expected_start_time is None:
                    current.expected_start_time = time
                else:
                    yield current
                    current = UpcomingInstance(journey=journey, expected_start_time=time)
            else:
                current.expected_end_time = time
                yield current
                current = UpcomingInstance(journey=journey)
        if current.expected_start_time or current.expected_end_time:
            yield current
