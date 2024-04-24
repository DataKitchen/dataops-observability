__all__ = ["MetricEntry", "MetricEntrySchema", "MetricLog", "MetricLogSchema", "MetricLogUserEvent"]

from dataclasses import dataclass
from decimal import Decimal as std_Decimal
from typing import Any

from marshmallow import Schema, post_load
from marshmallow.fields import Decimal, Nested, Str

from ...entities.event import ApiEventType
from ...schemas.validators import not_empty
from ..event_handler import EventHandlerBase
from ..v2.base import EventV2
from .base import BasePayload, BasePayloadSchema, EventV2
from .component_data import ComponentData, ComponentDataSchema


@dataclass
class MetricEntry:
    key: str
    value: std_Decimal


@dataclass
class MetricLog(BasePayload):
    component: ComponentData
    metric_entries: list[MetricEntry]


class MetricEntrySchema(Schema):
    key = Str(
        required=True,
        validate=not_empty(),
        metadata={
            "description": (
                "Required. A string to identify the metric_value data source. Used to group like metrics. This value "
                "is created and managed by the user."
            ),
            "example": "aaff79f0-5e10-4038-b847-28c0e5f42f0d",
        },
    )
    value = Decimal(
        required=True,
        allow_nan=False,
        as_string=True,
        metadata={
            "description": "Required. The data value to be logged. Decimal numerals only; NaN/INF values not supported.",
            "example": 10.22,
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> MetricEntry:
        return MetricEntry(**data)


class MetricLogSchema(BasePayloadSchema):
    component = Nested(
        ComponentDataSchema,
        required=True,
        metadata={"description": "Required. The component associated to the log entries."},
    )
    metric_entries = Nested(
        MetricEntrySchema,
        required=True,
        validate=not_empty(),
        many=True,
        metadata={"description": "Optional. A list of metric values."},
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> MetricLog:
        return MetricLog(**data)


@dataclass(kw_only=True)
class MetricLogUserEvent(EventV2):
    event_payload: MetricLog
    event_type: ApiEventType = ApiEventType.METRIC_LOG

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_metric_log_v2(self)
