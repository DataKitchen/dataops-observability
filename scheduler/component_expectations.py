import logging
from datetime import datetime, timedelta
from uuid import UUID

from apscheduler.triggers.cron import CronTrigger

from common.apscheduler_extensions import DelayedTrigger, fix_weekdays
from common.entities import Schedule, ScheduleExpectation
from common.events.enums import ScheduleType
from common.events.internal import ScheduledEvent
from common.kafka import TOPIC_SCHEDULED_EVENTS
from scheduler.schedule_source import ScheduleSource

LOG = logging.getLogger(__name__)


class ComponentScheduleSource(ScheduleSource[Schedule]):
    source_name = "component_expectations"
    kafka_topic = TOPIC_SCHEDULED_EVENTS

    def _get_schedules(self) -> list[Schedule]:
        return list(Schedule.select())

    def _produce_event(
        self,
        run_time: datetime,
        schedule_id: UUID,
        component_id: UUID,
        schedule_type: ScheduleType,
        is_margin: bool,
        margin: int | None = None,
    ) -> None:
        """Create and forward corresponding scheduler event(s) to the run manager"""
        if is_margin:
            if not margin:
                raise ValueError("'margin' must be set when 'is_margin' is True")
            schedule_timestamp = run_time - timedelta(seconds=margin)
            schedule_margin = run_time
        else:
            schedule_timestamp = run_time
            schedule_margin = None
            if margin:
                schedule_margin = run_time + timedelta(seconds=margin)

        event = ScheduledEvent(
            schedule_id=schedule_id,
            component_id=component_id,
            schedule_type=schedule_type,
            schedule_timestamp=schedule_timestamp,
            schedule_margin=schedule_margin,
        )

        LOG.info("Producing event: %s", event)
        self.event_producer.produce(self.kafka_topic, event)

    def _create_and_add_job(self, schedule: Schedule) -> None:
        common_job_args = {
            "schedule_id": schedule.id,
            "component_id": schedule.component_id,
            "margin": schedule.margin,
            "is_margin": False,
            "run_time": None,  # to be updated later
        }

        trigger = CronTrigger.from_crontab(fix_weekdays(schedule.schedule), timezone=schedule.timezone)

        if schedule.expectation == ScheduleExpectation.BATCH_PIPELINE_START_TIME.value:
            self.add_job(
                self._produce_event,
                job_id=f"{schedule.id}:{ScheduleType.BATCH_START_TIME.value}",
                trigger=trigger,
                kwargs={**common_job_args, "schedule_type": ScheduleType.BATCH_START_TIME},
            )

            margin_trigger = DelayedTrigger(trigger, delay=timedelta(seconds=schedule.margin))
            self.add_job(
                self._produce_event,
                job_id=f"{schedule.id}:{ScheduleType.BATCH_START_TIME_MARGIN.value}",
                trigger=margin_trigger,
                kwargs={**common_job_args, "schedule_type": ScheduleType.BATCH_START_TIME_MARGIN, "is_margin": True},
            )

        elif schedule.expectation == ScheduleExpectation.BATCH_PIPELINE_END_TIME.value:
            self.add_job(
                self._produce_event,
                job_id=f"{schedule.id}:{ScheduleType.BATCH_END_TIME.value}",
                trigger=trigger,
                kwargs={**common_job_args, "schedule_type": ScheduleType.BATCH_END_TIME},
            )

        elif schedule.expectation == ScheduleExpectation.DATASET_ARRIVAL.value:
            margin_trigger = DelayedTrigger(trigger, delay=timedelta(seconds=schedule.margin))
            self.add_job(
                self._produce_event,
                job_id=f"{schedule.id}:{ScheduleType.DATASET_ARRIVAL_MARGIN.value}",
                trigger=margin_trigger,
                kwargs={**common_job_args, "schedule_type": ScheduleType.DATASET_ARRIVAL_MARGIN, "is_margin": True},
            )

        else:
            LOG.error(
                "Expectation '%s' doesn't match any of %s", schedule.expectation, {e.value for e in ScheduleExpectation}
            )
