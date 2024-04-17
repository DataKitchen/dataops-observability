__all__ = ["RunSchema", "RunSummarySchema", "TestOutcomeSummarySchema"]

from typing import Union

from marshmallow import Schema, post_dump
from marshmallow.fields import DateTime, Int, List, Nested, Str

from common.constants import MAX_RUN_KEY_LENGTH
from common.entities.run import Run
from common.entities.task import RunTaskStatus
from common.events.v1 import TestStatuses
from common.schemas.fields import EnumStr
from common.schemas.validators import not_empty
from observability_api.schemas import RunAlertSchema
from observability_api.schemas.base_schemas import BaseEntitySchema
from observability_api.schemas.pipeline_schemas import PipelineSchema
from observability_api.schemas.task_schemas import TaskSummarySchema


# This schema belongs to testoutcome but has to be defined here to avoid circular dependency
# since test_outcome_schemas.py imports RunSummarySchema
class TestOutcomeSummarySchema(Schema):
    status = EnumStr(enum=TestStatuses, required=True)
    count = Int(data_key="count", required=True)


class RunSchema(BaseEntitySchema):
    pipeline = Nested(PipelineSchema(only=["id", "key", "display_name", "tool"]))
    key = Str(validate=not_empty(max=MAX_RUN_KEY_LENGTH))
    name = Str()
    run_tasks = List(Nested(TaskSummarySchema()), data_key="tasks_summary", dump_only=True)
    run_alerts = List(Nested(RunAlertSchema()), data_key="alerts", dump_only=True)
    test_outcome_run = List(Nested(TestOutcomeSummarySchema()), data_key="tests_summary", dump_only=True)
    start_time = DateTime(dump_only=True)
    end_time = DateTime(dump_only=True)
    expected_start_time = DateTime(
        dump_only=True,
        metadata={
            "description": "Optional. The timestamp representing the time the system expected a PENDING or MISSING next run to achieve the RUNNING status."
        },
    )
    expected_end_time = DateTime(
        dump_only=True,
        metadata={
            "description": "Optional. The timestamp representing the time the system expected a PENDING or MISSING next run to achieve a completed status."
        },
    )

    @post_dump(pass_many=True)
    def add_task_statuses(self, data: Union[list[dict], dict], **kwargs: dict) -> Union[list[dict], dict]:
        """Add missing task statuses that are not represented in the run"""
        all_statuses = RunTaskStatus.as_set()
        for run in data if isinstance(data, list) else [data]:
            if (tasks_summary := run.get("tasks_summary")) is not None:
                missing_task_statuses = all_statuses - {a["status"] for a in tasks_summary}
                for s in missing_task_statuses:
                    tasks_summary.append({"status": s, "count": 0})
        return data

    class Meta:
        model = Run


class RunSummarySchema(Schema):
    status = Str(required=True)
    count = Int(required=True)
