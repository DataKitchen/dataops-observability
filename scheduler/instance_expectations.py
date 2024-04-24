import logging
from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from peewee import Select

from common.apscheduler_extensions import fix_weekdays
from common.entities import InstanceRule, InstanceRuleAction
from common.events.internal.scheduled_instance import ScheduledInstance
from common.kafka import TOPIC_SCHEDULED_EVENTS
from scheduler.schedule_source import ScheduleSource

LOG = logging.getLogger(__name__)


class InstanceScheduleSource(ScheduleSource):
    source_name = "instance_expectations"
    kafka_topic = TOPIC_SCHEDULED_EVENTS

    def _get_schedules(self) -> Select:
        return InstanceRule.select().where(InstanceRule.expression.is_null(False))

    def _produce_event(
        self,
        run_time: datetime,
        instance_rule: InstanceRule,
    ) -> None:
        """Create and forward corresponding scheduler event(s) to the run manager"""
        event = ScheduledInstance(
            project_id=instance_rule.journey.project.id,
            journey_id=instance_rule.journey.id,
            instance_rule_id=instance_rule.id,
            instance_rule_action=instance_rule.action,
            timestamp=run_time,
        )
        LOG.info("Producing event: %s", event)
        self.event_producer.produce(self.kafka_topic, event)

    def _create_and_add_job(self, instance_rule: InstanceRule) -> None:
        trigger = CronTrigger.from_crontab(fix_weekdays(instance_rule.expression), timezone=instance_rule.timezone)
        if instance_rule.action in InstanceRuleAction:
            self.add_job(
                self._produce_event,
                job_id=f"{instance_rule.id}:{instance_rule.action.value}",
                trigger=trigger,
                kwargs={"instance_rule": instance_rule, "run_time": None},
            )
        else:
            LOG.error(
                "Instance expectation '%s' must match one of these values %s",
                instance_rule.action,
                set(action.value for action in InstanceRuleAction),
            )
