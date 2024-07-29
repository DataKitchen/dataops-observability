__all__ = ["InstanceDagSchema", "InstanceDagNodeSchema"]

from marshmallow import Schema
from marshmallow.fields import List, Nested, Str

from observability_api.schemas.alert_schemas import AlertSummarySchema
from observability_api.schemas.component_schemas import ComponentSchema
from observability_api.schemas.dataset_schemas import DatasetOperationsSummarySchema
from observability_api.schemas.journey_dag_schemas import JourneyDagEdgeCompactSchema
from observability_api.schemas.run_schemas import RunSummarySchema, TestOutcomeSummarySchema


class InstanceDagNodeSchema(Schema):
    component = Nested(ComponentSchema, only=["id", "key", "name", "display_name", "type", "tool"], required=True)
    status = Str(required=True)
    edges = Nested(JourneyDagEdgeCompactSchema, required=True, many=True)
    runs_summary = List(
        Nested(RunSummarySchema()),
        dump_default=list,
        dump_only=True,
        metadata={"description": "The summary of the runs."},
    )
    alerts_summary = List(
        Nested(AlertSummarySchema()),
        dump_default=list,
        dump_only=True,
        metadata={"description": "The run-level and instance-level alerts summary of the instance"},
    )
    tests_summary = List(
        Nested(TestOutcomeSummarySchema()),
        dump_default=list,
        dump_only=True,
        metadata={"description": "The test summary of the instance."},
    )
    operations_summary = List(
        Nested(DatasetOperationsSummarySchema()),
        dump_default=list,
        dump_only=True,
        metadata={"description": "The summary of dataset operations."},
    )


class InstanceDagSchema(Schema):
    nodes = List(Nested(InstanceDagNodeSchema), required=True)
