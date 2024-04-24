__all__ = ["RunAlertSchema", "InstanceAlertSchema", "AlertSummarySchema", "UIAlertSchema"]

from itertools import chain

from marshmallow import Schema, pre_dump
from marshmallow.fields import UUID, DateTime, Dict, Int, List, Nested, Pluck, String
from marshmallow.validate import Length
from marshmallow_peewee import ModelSchema

from common.datetime_utils import timestamp_to_datetime
from common.entities import InstanceAlertType
from common.entities.alert import AlertLevel, InstanceAlert, RunAlert, RunAlertType
from common.schemas.fields import EnumStr

from .base_schemas import BaseEntitySchema
from .component_schemas import ComponentSchema


class BaseAlertSchema(Schema):
    created_on = DateTime(
        required=True,
        dump_only=True,
        metadata={"description": "Required. The time (in UTC) when the incident was detected."},
    )
    level = EnumStr(
        required=True, enum=AlertLevel, metadata={"description": "Required. The severity-level of the alert."}
    )
    description = String(
        required=True,
        validate=Length(max=255),
        metadata={"description": "Required: A short explanation of the incident that generated the alert."},
    )
    name = String(required=False, validate=Length(max=255))
    details = Dict(
        required=False,
        metadata={"description": "Optional. Data contextualizing the alert."},
    )


class AlertSummarySchema(Schema):
    level = EnumStr(enum=AlertLevel)
    description = String()
    count = Int()


class RunAlertSchema(BaseAlertSchema, BaseEntitySchema):
    type = EnumStr(required=True, enum=RunAlertType)

    class Meta:
        model = RunAlert


class InstanceAlertsComponentsSchema(ModelSchema):
    component = Nested(ComponentSchema(only=["id", "type", "display_name", "tool"]), required=True)


class InstanceAlertSchema(BaseAlertSchema, ModelSchema):
    type = EnumStr(required=True, enum=InstanceAlertType)
    components = List(Pluck(InstanceAlertsComponentsSchema(), "component"), attribute="iac")

    class Meta:
        model = InstanceAlert


class ShortRunSchema(Schema):
    id = UUID()
    key = String()
    name = String()


class UIAlertSchema(Schema):
    level = EnumStr(dump_only=True, enum=AlertLevel, metadata={"description": "The severity-level of the alert."})
    description = String(
        dump_only=True,
        validate=Length(max=255),
        metadata={"description": "A short explanation of the incident that generated the alert."},
    )
    details = Dict(
        dump_only=True,
        metadata={"description": "Data contextualizing the alert."},
    )
    created_on = DateTime(
        dump_only=True,
        metadata={"description": "The time (in UTC) when the incident was detected."},
    )
    type = EnumStr(list(chain(RunAlertType.as_set(), InstanceAlertType.as_set())), required=True)
    run = Nested(ShortRunSchema(), dump_default=None)
    instance = UUID(attribute="instance_id", dump_default=None)
    components = List(Pluck(InstanceAlertsComponentsSchema(), "component"), attribute="iac", dump_default=None)

    @pre_dump(pass_many=True)
    def format_data(self, data: list[object], many: bool, **kwargs: object) -> list[object]:
        for d in data if many else [data]:
            setattr(d, "type", getattr(d, "type").name)
            if detail := getattr(d, "details"):
                if expected_start := detail.get("expected_start_time", None):
                    detail["expected_start_time"] = timestamp_to_datetime(expected_start).isoformat()
                if expected_end := detail.get("expected_end_time", None):
                    detail["expected_end_time"] = timestamp_to_datetime(expected_end).isoformat()
        return data
