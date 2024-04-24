import logging
from uuid import UUID

from common.entities import Instance, InstanceRuleAction
from common.entities.instance import InstanceStartType
from common.events.internal.scheduled_instance import ScheduledInstance

LOG = logging.getLogger(__name__)


def handle_scheduled_instance_event(event: ScheduledInstance) -> list[UUID | Instance]:
    memberships = [Instance.journey == event.journey_id, Instance.end_time.is_null(True)]
    if event.instance_rule_action == InstanceRuleAction.END_PAYLOAD:
        memberships.append(Instance.payload_key.is_null(False))
    else:
        memberships.append(Instance.payload_key.is_null(True))
    ended_instances = list(Instance.select().where(*memberships).execute())
    count = Instance.update({Instance.end_time: event.timestamp}).where(Instance.id.in_(ended_instances)).execute()
    LOG.info(
        "%d active instance closed by scheduled rule '%s' for journey '%s'",
        count,
        event.instance_rule_action,
        event.journey_id,
    )

    if event.instance_rule_action == InstanceRuleAction.START:
        # Start new instances
        instance = Instance.create(
            journey_id=event.journey_id, start_time=event.timestamp, start_type=InstanceStartType.SCHEDULED
        )
        LOG.info(
            "%s started by scheduled rule '%s' for journey '%s'", instance, event.instance_rule_action, event.journey_id
        )
    return ended_instances
