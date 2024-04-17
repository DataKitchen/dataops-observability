__all__ = [
    "InstanceAlert",
    "RunAlert",
]

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from common.decorators import cached_property
from common.entities import AlertLevel
from common.entities import InstanceAlert as InstanceAlertEntity
from common.entities import InstanceAlertType
from common.entities import RunAlert as RunAlertEntity
from common.entities import RunAlertType
from common.events.base import BatchPipelineMixin, EventBaseMixin, JourneyMixin, ProjectMixin


@dataclass(kw_only=True)
class AlertBase:
    alert_id: UUID
    level: AlertLevel
    description: Optional[str]


@dataclass(kw_only=True)
class RunAlert(EventBaseMixin, AlertBase, BatchPipelineMixin, ProjectMixin):
    type: RunAlertType

    @cached_property
    def alert(self) -> RunAlertEntity:
        _alert: RunAlertEntity = RunAlertEntity.get_by_id(self.alert_id)
        return _alert


@dataclass(kw_only=True)
class InstanceAlert(EventBaseMixin, AlertBase, JourneyMixin, ProjectMixin):
    type: InstanceAlertType

    @cached_property
    def alert(self) -> InstanceAlertEntity:
        _alert: InstanceAlertEntity = InstanceAlertEntity.get_by_id(self.alert_id)
        return _alert
