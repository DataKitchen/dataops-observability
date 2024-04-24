from __future__ import annotations

__all__ = ["RunStatusSchema", "RunStatusApiSchema", "RunStatusEvent", "ApiRunStatus"]

from dataclasses import dataclass
from enum import Enum
from typing import Any

from marshmallow import ValidationError, validates_schema

from common.constants.validation_messages import RUNSTATUS_EVENT_MISSING_REQUIRED_KEY
from common.decorators import cached_property
from common.entities import RunStatus
from common.events.event_handler import EventHandlerBase
from common.events.v1.event import PIPELINE_KEY_DETAILS, Event, EventComponentDetails
from common.events.v1.event_schemas import EventApiSchema, EventSchema
from common.schemas.fields import EnumStr


class ApiRunStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"


class RunStatusSchema(EventSchema):
    status = EnumStr(
        required=True,
        enum=RunStatus,
    )


class RunStatusApiSchema(EventApiSchema):
    status = EnumStr(
        required=True,
        enum=ApiRunStatus,
        metadata={
            "description": (
                "Required. The status to be applied. Can set the status for both runs and tasks. "
                "A run starts when no task_key is present and status is “RUNNING” and ends when no "
                "task_key is present and status is not running."
            )
        },
    )

    @validates_schema
    def validate_pipeline_key(self, data: dict[str, Any], **_: Any) -> None:
        # RunStatusEvent must have both `pipeline_key` and `run_key` specified
        if not data.get("pipeline_key", None) or not data.get("run_key", None):
            raise ValidationError(RUNSTATUS_EVENT_MISSING_REQUIRED_KEY)

    pass


@dataclass
class RunStatusEvent(Event):
    """Indicates that an open run should be closed."""

    __schema__ = RunStatusSchema
    __api_schema__ = RunStatusApiSchema

    status: str

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_run_status(self)

    @property
    def is_close_run(self) -> bool:
        """Determine if this is a close-run event."""
        if self.task_key:
            return False
        if RunStatus.is_end_status(self.status):
            return True
        return False

    @cached_property
    def component_key_details(self) -> EventComponentDetails:
        return PIPELINE_KEY_DETAILS
