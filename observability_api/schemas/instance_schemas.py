__all__ = ["InstanceSchema", "InstanceDetailedSchema"]

from marshmallow import pre_dump, Schema
from marshmallow.fields import Bool, DateTime, List, Nested, Pluck, Str

from common.entities import Instance, InstanceStatus
from common.entities.instance import InstanceStartType
from common.schemas.fields import EnumStr
from observability_api.schemas.alert_schemas import AlertSummarySchema
from observability_api.schemas.base_schemas import BaseEntitySchema
from observability_api.schemas.journey_schemas import JourneyProjectSchema, JourneySchema
from observability_api.schemas.run_schemas import RunSummarySchema, TestOutcomeSummarySchema


class InstanceSchema(BaseEntitySchema):
    journey = Nested(JourneySchema, only=["id", "name"], dump_only=True)
    # project property is using the journeySchema because the Instance object doesn't have a project, it's nested inside the journey.
    # Therefore we pick it out of the journey's object using it's schema definition. We are only interested in the project property of that schema
    # hence Pluck(..., "project" ...) and that the data should be looked up on the instance's journey attribute, not project.
    # See https://marshmallow.readthedocs.io/en/latest/marshmallow.fields.html#marshmallow.fields.Pluck for a simpler example.
    # On JourneySchema project is also a schema instead of a primitive, so the project schema will get used and generate a dict based on it.
    project = Pluck(JourneyProjectSchema, "project", attribute="journey", dump_only=True)
    start_time = DateTime(dump_only=True)
    end_time = DateTime(dump_only=True)
    expected_end_time = DateTime(dump_only=True, dump_default=None)
    active = Bool(dump_only=True)
    status = EnumStr(InstanceStatus, dump_only=True)
    payload_key = Str(dump_only=True)
    start_type = EnumStr(InstanceStartType, dump_only=True)


class InstanceDetailedSchema(InstanceSchema):
    runs_summary = List(
        Nested(RunSummarySchema()),
        dump_only=True,
        metadata={"description": "The summary of the runs."},
    )
    alerts_summary = List(
        Nested(AlertSummarySchema()),
        dump_only=True,
        metadata={"description": "The run-level and instance-level alerts summary of the instance"},
    )
    tests_summary = List(
        Nested(TestOutcomeSummarySchema()),
        dump_only=True,
        metadata={"description": "The test summary of the instance."},
    )

    @pre_dump
    def adjust_prefetched_run_alerts(self, instance: Instance, **_: object) -> Instance:
        if isinstance(instance.iis, list):
            instance.run_alerts = [iis.instance_set.run.runalert for iis in instance.iis]
        else:
            instance.run_alerts = []
        return instance
