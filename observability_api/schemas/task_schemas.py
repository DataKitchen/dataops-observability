__all__ = ["RunTaskSchema", "TaskSchema"]

from marshmallow import Schema
from marshmallow.fields import DateTime, Int, Nested, Str

from common.constants import MAX_TASK_KEY_LENGTH
from common.entities import RunTask, Task
from common.schemas.validators import not_empty
from observability_api.schemas.base_schemas import BaseEntitySchema


class TaskSchema(BaseEntitySchema):
    key = Str(validate=not_empty(max=MAX_TASK_KEY_LENGTH))
    name = Str(required=False)
    display_name = Str(dump_only=True)

    class Meta:
        model = Task


class RunTaskSchema(BaseEntitySchema):
    task = Nested(TaskSchema(only=["id", "key", "display_name"]))
    start_time = DateTime(dump_only=True)
    end_time = DateTime(dump_only=True)

    class Meta:
        model = RunTask


class TaskSummarySchema(Schema):
    status = Str(required=True)
    count = Int(required=True)
