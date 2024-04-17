__all__ = ["ScheduledEvent", "BatchPipelineStatusPlatformEvent"]

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from common.events.base import ComponentMixin
from common.events.enums import ScheduleType
from common.events.event_handler import EventHandlerBase
from common.events.v2 import BatchPipelineStatus
from common.events.v2.base import EventBase


@dataclass(kw_only=True)
class ScheduledEvent(ComponentMixin):
    """Represents an event emitted by the scheduler."""

    schedule_id: UUID
    schedule_type: ScheduleType
    schedule_timestamp: datetime
    schedule_margin: Optional[datetime] = None

    @property
    def partition_identifier(self) -> str:
        return str(self.component_id)


@dataclass(kw_only=True)
class BatchPipelineStatusPlatformEvent(EventBase):
    event_payload: BatchPipelineStatus

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_batch_pipeline_status_platform_v2(self)
