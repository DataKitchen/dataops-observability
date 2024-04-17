__all__ = ["ApiRunStatus", "BatchPipelineStatus", "BatchPipelineStatusSchema", "BatchPipelineStatusUserEvent"]

from dataclasses import dataclass
from enum import Enum as std_Enum
from typing import Any

from marshmallow import post_load
from marshmallow.fields import Enum, Nested

from common.entities import RunStatus
from common.entities.event import ApiEventType
from common.events.event_handler import EventHandlerBase
from common.events.v2.base import BasePayload, BasePayloadSchema, EventV2
from common.events.v2.component_data import BatchPipelineData, BatchPipelineDataSchema


@dataclass
class BatchPipelineStatus(BasePayload):
    batch_pipeline_component: BatchPipelineData
    status: RunStatus


class ApiRunStatus(std_Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"


class BatchPipelineStatusSchema(BasePayloadSchema):
    batch_pipeline_component = Nested(
        BatchPipelineDataSchema(),
        required=True,
        metadata={"description": "Required. The batch pipeline associated to the status."},
    )
    status = Enum(
        ApiRunStatus,
        required=True,
        metadata={
            "description": (
                "Required. The status to be applied. Can set the status for both runs and tasks. "
                "A run starts when no task_key is present and status is “RUNNING” and ends when no "
                "task_key is present and status is not running."
            )
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> BatchPipelineStatus:
        return BatchPipelineStatus(status=RunStatus(data.pop("status").name), **data)


@dataclass(kw_only=True)
class BatchPipelineStatusUserEvent(EventV2):
    event_payload: BatchPipelineStatus
    event_type: ApiEventType = ApiEventType.BATCH_PIPELINE_STATUS

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_batch_pipeline_status_user_v2(self)
