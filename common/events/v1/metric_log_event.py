__all__ = ["MetricLogSchema", "MetricLogApiSchema", "MetricLogEvent"]

from dataclasses import dataclass
from decimal import Decimal as std_decimal

from marshmallow import Schema
from marshmallow.fields import Decimal, Str

from common.events.event_handler import EventHandlerBase
from common.events.v1.event import Event
from common.events.v1.event_schemas import EventApiSchema, EventSchema
from common.schemas.validators import not_empty


class MetricLogBaseSchema(Schema):
    metric_key = Str(
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
    metric_value = Decimal(
        required=True,
        allow_nan=False,
        # As string because Decimal is not serializable
        as_string=True,
        metadata={
            "description": "Required. The data value to be logged. Decimal numerals only; NaN/INF values not supported.",
            "example": 10.22,
        },
    )


class MetricLogSchema(MetricLogBaseSchema, EventSchema):
    pass


class MetricLogApiSchema(MetricLogBaseSchema, EventApiSchema):
    pass


@dataclass
class MetricLogEvent(Event):
    """Represents the log of a value of a user-defined datum."""

    metric_key: str
    metric_value: std_decimal

    __schema__ = MetricLogSchema
    __api_schema__ = MetricLogApiSchema

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_metric_log(self)
