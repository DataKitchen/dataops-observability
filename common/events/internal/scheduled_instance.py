__all__ = [
    "ScheduledInstance",
]

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from common.entities import InstanceRuleAction
from common.events.base import ProjectMixin


@dataclass(kw_only=True)
class ScheduledInstance(ProjectMixin):
    journey_id: UUID
    instance_rule_id: UUID
    instance_rule_action: InstanceRuleAction
    timestamp: datetime
