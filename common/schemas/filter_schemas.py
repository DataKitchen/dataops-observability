from datetime import datetime, timezone
from typing import Any, Optional, Union

from marshmallow import EXCLUDE, Schema, ValidationError, pre_load, validates_schema
from marshmallow.fields import UUID, AwareDateTime, Boolean, Enum, List, Str
from werkzeug.datastructures import MultiDict

from common.entities import InstanceStatus
from common.schemas.validators import not_empty


class FiltersSchema(Schema):
    def validate_time_range(
        self, range_begin: Optional[datetime], range_end: Optional[datetime], range_begin_name: str
    ) -> None:
        if range_begin is None or range_end is None:
            return None
        if range_begin >= range_end:
            raise ValidationError({range_begin_name: "Invalid range. Time range begins after range ends."})

    class Meta:
        unknown = EXCLUDE


class InstanceFiltersSchema(FiltersSchema):
    journey_ids = List(
        UUID(
            metadata={
                "description": "Optional. Specifies which journeys to include by their ID. All journeys are selected if unset."
            },
        ),
        data_key="journey_id",
    )
    active = Boolean(
        allow_none=True,
        metadata={
            "description": "Optional. When true, instances without a reported end_time are returned i.e., uncompleted "
            "instances. When active is false, instances with a reported end_time are returned i.e., "
            "completed instances. Leave this query unspecified to return instances with both states. Cannot "
            "be specified with end_range_begin or end_range_end."
        },
    )
    start_range_begin = AwareDateTime(
        allow_none=True,
        format="iso",
        default_timezone=timezone.utc,
        metadata={
            "description": "Optional. An ISO8601 datetime. If specified, The result will only include instances with a "
            "start_time field equal or past the given datetime. May be specified with start_range_end "
            "to create a range."
        },
    )
    start_range_end = AwareDateTime(
        allow_none=True,
        format="iso",
        default_timezone=timezone.utc,
        metadata={
            "description": "Optional. An ISO8601 datetime. If specified, the result will only contain instances with a "
            "start_time field before the given datetime. May be specified with start_range_begin to create "
            "a range."
        },
    )
    end_range_begin = AwareDateTime(
        allow_none=True,
        format="iso",
        default_timezone=timezone.utc,
        metadata={
            "description": "Optional. An ISO8601 datetime. If specified, The result will only include instances with an "
            "end_time field equal or past the given datetime. May be specified with end_range_end to create a range."
        },
    )
    end_range_end = AwareDateTime(
        allow_none=True,
        format="iso",
        default_timezone=timezone.utc,
        metadata={
            "description": "Optional. An ISO8601 datetime. If specified, The result will only include instances with an "
            "end_time field before the given datetime. May be specified with end_range_begin to create a range."
        },
    )
    journey_names = List(
        Str(
            validate=not_empty(),
            metadata={
                "description": "Optional. If specified, the results will be limited to instances with the journeys named."
            },
        ),
        data_key="journey_name",
    )
    statuses = List(
        Enum(
            InstanceStatus,
            metadata={
                "description": "Optional. If specified, the results will be limited to instances with the specified statuses."
            },
        ),
        data_key="status",
    )

    @pre_load(pass_many=False)
    def from_multidict(self, data: Union[dict, MultiDict], **_: Any) -> dict:
        if isinstance(data, MultiDict):
            return {
                "journey_id": data.getlist("journey_id"),
                "active": data.get("active"),
                "start_range_begin": data.get("start_range_begin"),
                "start_range_end": data.get("start_range_end"),
                "end_range_begin": data.get("end_range_begin"),
                "end_range_end": data.get("end_range_end"),
                "journey_name": data.getlist("journey_name"),
                "status": data.getlist("status"),
                "project_id": data.getlist("project_id"),
            }
        return data

    @validates_schema(pass_many=False)
    def validate_filters(self, data: dict[str, Any], **_: Any) -> None:
        self.validate_time_range(data.get("start_range_begin"), data.get("start_range_end"), "start_range_begin")
        self.validate_time_range(data.get("end_range_begin"), data.get("end_range_end"), "end_range_begin")


class CompanyInstanceFiltersSchema(InstanceFiltersSchema):
    project_ids = List(
        UUID(
            metadata={
                "description": "Optional. Specifies the project IDs to include. All projects are selected if unset."
            }
        ),
        data_key="project_id",
    )
