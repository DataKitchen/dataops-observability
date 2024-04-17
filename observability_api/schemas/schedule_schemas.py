__all__ = ["ScheduleSchema"]

from typing import Any

from marshmallow import ValidationError, validates_schema
from marshmallow.fields import Integer, Pluck, Str

from common.constants.defaults import SCHEDULE_START_CRON_TIMEZONE
from common.constants.validation_messages import INVALID_SCHEDULE_MARGIN
from common.entities import Schedule, ScheduleExpectation
from common.schemas.fields import CronExpressionStr, EnumStr, ZoneInfo

from .base_schemas import AuditEntitySchemaMixin, BaseEntitySchema
from .component_schemas import ComponentSchema


def _validate_margin(value: Any) -> None:
    """Margin seconds has to match multiples of one minute."""
    if value == 0 or (value % 60) != 0:
        raise ValidationError(INVALID_SCHEDULE_MARGIN)


REQUIRE_MARGIN = {
    ScheduleExpectation.BATCH_PIPELINE_START_TIME.value,
    ScheduleExpectation.DATASET_ARRIVAL.value,
}
REQUIRE_MARGIN_STRING = "'" + "', '".join(REQUIRE_MARGIN) + "'"


class ScheduleSchema(AuditEntitySchemaMixin, BaseEntitySchema):
    component = Pluck(ComponentSchema, "id", dump_only=True)
    description = Str(
        metadata={
            "description": "An optional description of the schedule.",
        }
    )
    schedule = CronExpressionStr(
        required=True,
        metadata={
            "description": (
                "Required. A cron expression that defines when the 'expectation' should occur. Does not support cron "
                "extensions. Recommended minimum no less than 10 minutes."
            ),
            "example": "15 * * * 1,3,5",
        },
    )
    timezone = ZoneInfo(
        load_default=SCHEDULE_START_CRON_TIMEZONE,
        metadata={
            "description": (
                "Optional. The local timezone of the expression defined by the schedule parameter, "
                "as an IANA long or short database name. "
                f"If unspecified, the schedule defaults to '{SCHEDULE_START_CRON_TIMEZONE}'."
            ),
            "example": "America/Sao_Paulo",
        },
    )
    expectation = EnumStr(
        ScheduleExpectation,
        metadata={
            "description": "Required. Defines what is expected to happen at the given schedule.",
        },
    )
    margin = Integer(
        validate=_validate_margin,
        allow_none=True,
        metadata={
            "description": (
                "The expectation's margin-of-error in seconds, it must be expressed in increments of 60. "
                f"Required when 'expectation' is one of {REQUIRE_MARGIN_STRING}; disallowed otherwise. "
            )
        },
    )

    class Meta:
        model = Schedule

    @validates_schema
    def validate_start_time_margin(self, data: dict, **_: object) -> None:
        if data["expectation"] not in REQUIRE_MARGIN and data.get("margin") is not None:
            raise ValidationError(
                {"margin": [f"Setting a margin is only allowed for the '{REQUIRE_MARGIN_STRING}' expectations."]}
            )
        elif data["expectation"] in REQUIRE_MARGIN and data.get("margin") is None:
            raise ValidationError({"margin": [f"Margin is required for '{REQUIRE_MARGIN_STRING}' expectations."]})
