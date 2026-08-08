from __future__ import annotations

__all__ = ["DatasetOperationSchema", "DatasetOperationApiSchema", "DatasetOperationEvent", "DatasetOperationType"]

from dataclasses import dataclass

from marshmallow import Schema, ValidationError, validates_schema
from marshmallow.fields import Str

from common.entities.dataset_operation import DatasetOperationType
from common.events.event_handler import EventHandlerBase
from common.events.v1.event import Event
from common.events.v1.event_schemas import EventApiSchema, EventSchema
from common.schemas.fields import EnumStr
from common.schemas.validators import not_empty


class DatasetOperationBaseSchema(Schema):
    operation = EnumStr(
        required=True,
        enum=DatasetOperationType,
        metadata={
            "description": "Required. The read or write operation performed.",
        },
    )
    path = Str(
        load_default=None,
        validate=not_empty(max=4096),
        metadata={
            "description": "Optional. Path within the dataset where the operation took place.",
            "example": "path/to/file",
        },
    )


class DatasetOperationSchema(DatasetOperationBaseSchema, EventSchema):
    pass


class DatasetOperationApiSchema(DatasetOperationBaseSchema, EventApiSchema):
    @validates_schema
    def validate_keys(self, data: dict, **_: object) -> None:
        invalid = {k: [f"{k} must not be set"] for k in ("pipeline_key", "run_key") if data.get(k) is not None}
        if data.get("dataset_key") is None:
            invalid["dataset_key"] = ["dataset_key must be set."]

        if invalid:
            raise ValidationError(invalid)


@dataclass
class DatasetOperationEvent(Event):
    __schema__ = DatasetOperationSchema
    __api_schema__ = DatasetOperationApiSchema

    operation: str
    path: str | None = None

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_dataset_operation(self)
