from enum import Enum as EnumType

from marshmallow import Schema, ValidationError, post_dump, validates_schema
from marshmallow.fields import Bool, Decimal, Enum, Int, List, Nested, Str
from marshmallow.validate import Range

from common.entities import AlertLevel, InstanceAlertType, RunState, RunStatus
from common.events.v1 import MessageEventLogLevel, TestStatuses
from common.schemas.fields import EnumStr
from common.schemas.validators import IsRegexp, not_empty


class RunStatusConditionSchema(Schema):
    matches = EnumStr(
        enum=RunStatus,
        required=False,
        metadata={"description": "The run status to match against."},
    )


class RunStateConditionSchema(Schema):
    matches = Enum(
        enum=RunState,
        required=False,
        metadata={"description": "The run state to match against."},
    )
    count = Int(
        required=False,
        load_default=1,
        validate=Range(min=1, max=250),
        metadata={"description": "How many consecutive runs should match the run state"},
    )
    trigger_successive = Bool(
        required=False,
        load_default=True,
        metadata={"description": "Trigger on successive matching runs after count is achieved"},
    )
    group_run_name = Bool(
        required=False,
        load_default=False,
        metadata={"description": "Check consecutive runs where run_name matches"},
    )

    @validates_schema
    def reject_unsupported_counts(self, data: dict, **_: object) -> None:
        if data["matches"] is RunState.RUNNING:
            if data["count"] > 1:
                raise ValidationError(f"Run state {data['matches']} cannout be used with a count above 1")
            elif data["trigger_successive"] is False:
                raise ValidationError(f"Run state {data['matches']} cannout be used when trigger_successive is false")


class MetricValueOperator(EnumType):
    EXACT = "EXACT"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"


class MetricConditionSchema(Schema):
    key = Str(
        required=True,
        validate=not_empty(),
        metadata={
            "description": (
                "Required. The string value that identifies the metric. This value is created and managed by the user."
            ),
            "example": "cpu_usage",
        },
    )
    operator = EnumStr(
        enum=MetricValueOperator,
        required=True,
    )
    static_value = Decimal(
        required=True,
        allow_nan=False,
        # As string because Decimal is not serializable
        as_string=True,
        metadata={
            "description": "Required. The decimal value to be compared. NaN/INF values are not supported.",
            "example": 10.22,
        },
    )


class MessageConditionSchema(Schema):
    level = List(EnumStr(enum=MessageEventLogLevel), required=True)
    matches = Str(required=False, validate=IsRegexp())


class TestStatusConditionSchema(Schema):
    matches = EnumStr(enum=TestStatuses, required=False, metadata={"description": "The test status to match against."})


LEVEL_MATCHES_FIELD = List(EnumStr(enum=AlertLevel), required=False, load_default=[])


class InstanceAlertConditionSchema(Schema):
    level_matches = LEVEL_MATCHES_FIELD
    type_matches = List(EnumStr(enum=InstanceAlertType), required=False, load_default=[])


class ConditionSchema(Schema):
    VALID_KEYS: tuple[str, ...] = (
        "instance_alert",
        "message_log",
        "metric_log",
        "run_state",
        "task_status",
        "test_status",
    )

    instance_alert = Nested(InstanceAlertConditionSchema())
    message_log = Nested(MessageConditionSchema())
    metric_log = Nested(MetricConditionSchema())
    run_state = Nested(RunStateConditionSchema())
    task_status = Nested(RunStatusConditionSchema())
    test_status = Nested(TestStatusConditionSchema())

    @validates_schema
    def validate_rule_type_one_of(self, data: dict, **_: object) -> None:
        """Only one key is actually allowed."""
        if len(data) > 1:
            msg = f"Only one key may be present at a time. Got: {', '.join(data.keys())}"
            raise ValidationError({x: msg for x in self.VALID_KEYS})
        elif len(data) == 0:
            msg = f"Require at least one of the following keys: {', '.join(data.keys())}"
            raise ValidationError({x: msg for x in self.VALID_KEYS})

    @post_dump
    def remove_extra_key(self, data: dict, **_: object) -> dict:
        if data.get("run_state"):
            xor = set(self.VALID_KEYS) ^ {"run_state"}
        elif data.get("task_status"):
            xor = set(self.VALID_KEYS) ^ {"task_status"}
        elif data.get("message_log"):
            xor = set(self.VALID_KEYS) ^ {"message_log"}
        elif data.get("metric_log"):
            xor = set(self.VALID_KEYS) ^ {"metric_log"}
        elif data.get("test_status"):
            xor = set(self.VALID_KEYS) ^ {"test_status"}
        elif data.get("instance_alert"):
            xor = set(self.VALID_KEYS) ^ {"instance_alert"}
        for key in xor:
            data.pop(key, None)
        return data


class RuleDataSchema(Schema):
    when = EnumStr(
        enum=["any", "all"],
        required=True,
        normalizer=str.lower,
        metadata={
            "description": (
                "Required. Sets the relation between rules. If 'any' is specified, the action is triggered when one or"
                " more of the rules is positive (Boolean OR relationship). If 'all' is specified, the rule is triggered"
                " only when all of the rules are positive (Boolean AND relationship)."
            )
        },
    )
    conditions = List(
        Nested(ConditionSchema()),
        required=True,
        validate=not_empty(),
        metadata={"description": "Describes the conditions needed for the action to be triggered."},
    )
