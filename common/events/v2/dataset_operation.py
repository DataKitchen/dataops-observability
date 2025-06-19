__all__ = [
    "DatasetOperation",
    "DatasetOperationSchema",
    "DatasetOperationType",
    "DatasetOperationUserEvent",
]

from dataclasses import dataclass
from enum import Enum as std_Enum
from typing import Any

from marshmallow import post_load
from marshmallow.fields import Enum, Nested, Str

from common.entities.event import ApiEventType
from common.events.event_handler import EventHandlerBase
from common.events.v2.base import BasePayload, BasePayloadSchema, EventV2
from common.events.v2.component_data import DatasetData, DatasetDataSchema
from common.schemas.validators import not_empty


class DatasetOperationType(std_Enum):
    READ = "READ"
    WRITE = "WRITE"


@dataclass
class DatasetOperation(BasePayload):
    dataset_component: DatasetData
    operation: DatasetOperationType
    path: str | None


class DatasetOperationSchema(BasePayloadSchema):
    dataset_component = Nested(
        DatasetDataSchema,
        required=True,
        metadata={"description": "Required. The dataset associated to the operation."},
    )
    operation = Enum(
        DatasetOperationType,
        required=True,
        metadata={"description": ("Required. The read or write operation performed.")},
    )
    path = Str(
        load_default=None,
        validate=not_empty(max=4096),
        metadata={
            "description": "Optional. Path within the dataset where the operation took place.",
            "example": "path/to/file",
        },
    )

    @post_load
    def to_dataclass(self, data: dict, **_: Any) -> DatasetOperation:
        return DatasetOperation(**data)


@dataclass(kw_only=True)
class DatasetOperationUserEvent(EventV2):
    event_payload: DatasetOperation
    event_type: ApiEventType = ApiEventType.DATASET_OPERATION

    def accept(self, handler: EventHandlerBase) -> bool:
        return handler.handle_dataset_operation_v2(self)
