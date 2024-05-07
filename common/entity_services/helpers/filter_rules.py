from __future__ import annotations

__all__ = [
    "Filters",
    "AlertFilters",
    "ComponentFilters",
    "ProjectEventFilters",
    "RunFilters",
    "TestOutcomeItemFilters",
    "UpcomingInstanceFilters",
    "ActionFilters",
]

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, Type, TypeVar
from uuid import UUID

import arrow
from marshmallow import ValidationError
from werkzeug.datastructures import MultiDict

from common.api.request_parsing import str_to_bool
from common.entities import ActionImpl, ComponentType, InstanceStatus
from common.entities.event import ApiEventType
from common.schemas.fields import strip_upper_underscore

# Observability Runs API
START_RANGE_BEGIN_QUERY_NAME: str = "start_range_begin"
START_RANGE_END_QUERY_NAME: str = "start_range_end"
END_RANGE_BEGIN_QUERY_NAME: str = "end_range_begin"
END_RANGE_END_QUERY_NAME: str = "end_range_end"
START_RANGE_QUERY_NAME: str = "start_range"
END_RANGE_QUERY_NAME: str = "end_range"
ACTIVE_QUERY_NAME: str = "active"
PIPELINE_KEY_QUERY_NAME: str = "pipeline_key"
JOURNEY_NAMES_QUERY_NAME: str = "journey_name"
RUN_KEY_QUERY_NAME: str = "run_key"
KEY_QUERY_NAME: str = "key"

# List events endpoints
EVENT_TYPE_QUERY_NAME: str = "event_type"
EVENT_ID_QUERY_NAME: str = "event_id"
JOURNEY_ID_QUERY_NAME: str = "journey_id"
COMPONENT_ID_QUERY_NAME: str = "component_id"
RUN_ID_QUERY_NAME: str = "run_id"
INSTANCE_ID_QUERY_NAME: str = "instance_id"
TOOL_QUERY_NAME: str = "tool"
TASK_ID_QUERY_NAME: str = "task_id"
PROJECT_ID_QUERY_NAME: str = "project_id"
DATE_RANGE_START_QUERY_NAME: str = "date_range_start"
DATE_RANGE_END_QUERY_NAME: str = "date_range_end"

STATUS_QUERY_NAME: str = "status"
COMPONENT_TYPE_QUERY_NAME: str = "component_type"

# Alert endpoint
LEVEL_QUERY_NAME: str = "level"
TYPE_QUERY_NAME: str = "type"

# Action endpoint
ACTION_IMPL_QUERY_NAME: str = "action_impl"


F = TypeVar("F", bound="Filters")


@dataclass
class ParamConfig:
    member_name: str
    func: Callable


def _date_or_none(params: MultiDict, field_name: str) -> Optional[datetime]:
    if date := params.get(field_name):
        try:
            return arrow.get(date).datetime
        except arrow.ParserError as e:
            raise ValidationError({field_name: f"Invalid format. Expecting ISO-8601. Value: '{date}'"}) from e
    return None


def _str_to_bool(params: MultiDict, field_name: str) -> Optional[bool]:
    if (value := params.get(field_name)) is None:
        return None
    return str_to_bool(value, field_name)


def _normalize_tools(params: MultiDict, field_name: str) -> list[str]:
    return [strip_upper_underscore(t) for t in params.getlist(field_name)]


PARAM_CONFIGS = {
    ACTIVE_QUERY_NAME: ParamConfig("active", _str_to_bool),
    COMPONENT_ID_QUERY_NAME: ParamConfig("component_ids", MultiDict.getlist),
    COMPONENT_TYPE_QUERY_NAME: ParamConfig("component_types", MultiDict.getlist),
    DATE_RANGE_END_QUERY_NAME: ParamConfig("date_range_end", _date_or_none),
    DATE_RANGE_START_QUERY_NAME: ParamConfig("date_range_start", _date_or_none),
    END_RANGE_QUERY_NAME: ParamConfig("end_range", _date_or_none),
    END_RANGE_BEGIN_QUERY_NAME: ParamConfig("end_range_begin", _date_or_none),
    END_RANGE_END_QUERY_NAME: ParamConfig("end_range_end", _date_or_none),
    EVENT_ID_QUERY_NAME: ParamConfig("event_ids", MultiDict.getlist),
    EVENT_TYPE_QUERY_NAME: ParamConfig("event_types", MultiDict.getlist),
    INSTANCE_ID_QUERY_NAME: ParamConfig("instance_ids", MultiDict.getlist),
    JOURNEY_ID_QUERY_NAME: ParamConfig("journey_ids", MultiDict.getlist),
    JOURNEY_NAMES_QUERY_NAME: ParamConfig("journey_names", MultiDict.getlist),
    KEY_QUERY_NAME: ParamConfig("key", MultiDict.get),
    LEVEL_QUERY_NAME: ParamConfig("levels", MultiDict.getlist),
    PIPELINE_KEY_QUERY_NAME: ParamConfig("pipeline_keys", MultiDict.getlist),
    PROJECT_ID_QUERY_NAME: ParamConfig("project_ids", MultiDict.getlist),
    RUN_ID_QUERY_NAME: ParamConfig("run_ids", MultiDict.getlist),
    RUN_KEY_QUERY_NAME: ParamConfig("run_keys", MultiDict.getlist),
    START_RANGE_QUERY_NAME: ParamConfig("start_range", _date_or_none),
    START_RANGE_BEGIN_QUERY_NAME: ParamConfig("start_range_begin", _date_or_none),
    START_RANGE_END_QUERY_NAME: ParamConfig("start_range_end", _date_or_none),
    STATUS_QUERY_NAME: ParamConfig("statuses", MultiDict.getlist),
    TASK_ID_QUERY_NAME: ParamConfig("task_ids", MultiDict.getlist),
    TOOL_QUERY_NAME: ParamConfig("tools", _normalize_tools),
    TYPE_QUERY_NAME: ParamConfig("types", MultiDict.getlist),
    ACTION_IMPL_QUERY_NAME: ParamConfig("action_impls", MultiDict.getlist),
}


@dataclass
class Filters:
    """
    Base class for filter implementations

    Extend by specifying the wanted attributes and how to unpack them in from_params.
    """

    active: Optional[bool] = None
    component_ids: list[str] = field(default_factory=list)
    component_types: list[str] = field(default_factory=list)
    date_range_end: Optional[datetime] = None
    date_range_start: Optional[datetime] = None
    end_range: Optional[datetime] = None
    end_range_begin: Optional[datetime] = None
    end_range_end: Optional[datetime] = None
    event_ids: list[str] = field(default_factory=list)
    event_types: list[str] = field(default_factory=list)
    instance_ids: list[str] = field(default_factory=list)
    journey_ids: list[str] = field(default_factory=list)
    journey_names: list[str] = field(default_factory=list)
    key: Optional[str] = None
    levels: list[str] = field(default_factory=list)
    pipeline_keys: list[str] = field(default_factory=list)
    project_ids: list[str] = field(default_factory=list)
    run_ids: list[str] = field(default_factory=list)
    run_keys: list[str] = field(default_factory=list)
    start_range: Optional[datetime] = None
    start_range_begin: Optional[datetime] = None
    start_range_end: Optional[datetime] = None
    statuses: list[str] = field(default_factory=list)
    task_ids: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    types: list[str] = field(default_factory=list)
    action_impls: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        for data in self.__dataclass_fields__.keys():
            field = getattr(self, data)
            if field is not None and field != []:
                return True
        return False

    @staticmethod
    def validate_time_range(
        range_begin: Optional[datetime], range_end: Optional[datetime], range_begin_name: str
    ) -> None:
        if range_begin is None or range_end is None:
            return None
        if range_begin >= range_end:
            raise ValidationError({range_begin_name: "Invalid range. Time range begins after range ends."})

    @staticmethod
    def validate_event_types(event_types: list[str]) -> None:
        invalid_events = [event for event in event_types if event not in ApiEventType.__members__]
        if invalid_events:
            raise ValidationError(
                {
                    invalid: "Invalid 'event_type' query parameter. Consult the API Documentation."
                    for invalid in invalid_events
                }
            )

    @staticmethod
    def validate_component_types(component_types_param: list[str]) -> None:
        COMPONENT_TYPES = [comp_type.name for comp_type in ComponentType]
        invalid_components = [c for c in component_types_param if c not in COMPONENT_TYPES]
        if invalid_components:
            raise ValidationError(
                {
                    invalid: "Invalid 'component_type' query parameter. Consult the API Documentation."
                    for invalid in invalid_components
                }
            )

    @staticmethod
    def validate_instance_status(statuses: list[str]) -> None:
        invalid_stt = [stt for stt in statuses if stt not in InstanceStatus.as_set()]
        if invalid_stt:
            raise ValidationError(
                {invalid: "Invalid 'status' query parameter. Consult the API Documentation." for invalid in invalid_stt}
            )

    @staticmethod
    def validate_action_impls(action_impls_param: list[str]) -> None:
        ACTION_IMPLS = [action_impl.name for action_impl in ActionImpl]
        invalid_impls = [a for a in action_impls_param if a not in ACTION_IMPLS]
        if invalid_impls:
            raise ValidationError(
                {
                    invalid: "Invalid 'action_impl' query parameter. Consult the API Documentation."
                    for invalid in invalid_impls
                }
            )

    @classmethod
    def from_params(cls, params: MultiDict) -> Filters:
        raise NotImplementedError

    @classmethod
    def from_dict(cls: Type[F], data: dict) -> F:
        return cls(**data)

    @classmethod
    def _from_params(cls: Type[F], params: MultiDict, param_names: list[str]) -> F:
        members = {}
        for set_parameter in param_names:
            if (param_config := PARAM_CONFIGS.get(set_parameter, None)) is None:
                raise ValueError(f"Parameter {set_parameter} is not valid")
            members[param_config.member_name] = param_config.func(params, set_parameter)

        return cls(**members)


@dataclass
class RunFilters(Filters):
    """
    This is utilized for taking in the query parameters related to filtering Run entities
    """

    @classmethod
    def from_params(cls, params: MultiDict) -> RunFilters:
        filters = cls._from_params(
            params,
            [
                START_RANGE_BEGIN_QUERY_NAME,
                START_RANGE_END_QUERY_NAME,
                END_RANGE_BEGIN_QUERY_NAME,
                END_RANGE_END_QUERY_NAME,
                PIPELINE_KEY_QUERY_NAME,
                RUN_KEY_QUERY_NAME,
                STATUS_QUERY_NAME,
                COMPONENT_ID_QUERY_NAME,
                INSTANCE_ID_QUERY_NAME,
                TOOL_QUERY_NAME,
            ],
        )

        cls.validate_time_range(filters.start_range_begin, filters.start_range_end, START_RANGE_BEGIN_QUERY_NAME)
        cls.validate_time_range(filters.end_range_begin, filters.end_range_end, END_RANGE_BEGIN_QUERY_NAME)
        return filters


@dataclass
class ComponentFilters(Filters):
    """
    This is utilized for taking in the query parameters related to filtering Components entities
    """

    @classmethod
    def from_params(cls, params: MultiDict) -> ComponentFilters:
        filters = cls._from_params(
            params,
            [
                COMPONENT_TYPE_QUERY_NAME,
                TOOL_QUERY_NAME,
            ],
        )
        cls.validate_component_types(filters.component_types)
        return filters


@dataclass
class TestOutcomeItemFilters(Filters):
    """This is utilized for taking in the query parameters related to filtering test outcome entities."""

    @classmethod
    def from_params(cls, params: MultiDict) -> TestOutcomeItemFilters:
        filters = cls._from_params(
            params,
            [
                COMPONENT_ID_QUERY_NAME,
                END_RANGE_BEGIN_QUERY_NAME,
                END_RANGE_END_QUERY_NAME,
                INSTANCE_ID_QUERY_NAME,
                KEY_QUERY_NAME,
                RUN_ID_QUERY_NAME,
                START_RANGE_BEGIN_QUERY_NAME,
                START_RANGE_END_QUERY_NAME,
                STATUS_QUERY_NAME,
            ],
        )

        cls.validate_time_range(filters.start_range_begin, filters.start_range_end, START_RANGE_BEGIN_QUERY_NAME)
        cls.validate_time_range(filters.end_range_begin, filters.end_range_end, END_RANGE_BEGIN_QUERY_NAME)
        return filters


@dataclass
class ProjectEventFilters(Filters):
    """
    This is utilized for taking in the query parameters related to "filtering" Event entities in Projects list events endpoint.
    """

    @classmethod
    def from_params(cls, params: MultiDict, project_ids: list[UUID] = []) -> ProjectEventFilters:
        filters = cls._from_params(
            params,
            [
                EVENT_TYPE_QUERY_NAME,
                EVENT_ID_QUERY_NAME,
                RUN_ID_QUERY_NAME,
                JOURNEY_ID_QUERY_NAME,
                COMPONENT_ID_QUERY_NAME,
                INSTANCE_ID_QUERY_NAME,
                TASK_ID_QUERY_NAME,
                DATE_RANGE_START_QUERY_NAME,
                DATE_RANGE_END_QUERY_NAME,
            ],
        )

        filters.project_ids = [str(u) for u in project_ids]

        cls.validate_event_types(filters.event_types)
        cls.validate_time_range(filters.date_range_start, filters.date_range_end, DATE_RANGE_START_QUERY_NAME)
        return filters


@dataclass
class AlertFilters(Filters):
    """
    This is utilized for taking in the query parameters related to filtering test outcome entities
    """

    @classmethod
    def from_params(cls, params: MultiDict) -> AlertFilters:
        filters = cls._from_params(
            params,
            [
                INSTANCE_ID_QUERY_NAME,
                RUN_ID_QUERY_NAME,
                RUN_KEY_QUERY_NAME,
                LEVEL_QUERY_NAME,
                TYPE_QUERY_NAME,
                COMPONENT_ID_QUERY_NAME,
                DATE_RANGE_START_QUERY_NAME,
                DATE_RANGE_END_QUERY_NAME,
            ],
        )

        cls.validate_time_range(filters.date_range_start, filters.date_range_end, DATE_RANGE_START_QUERY_NAME)
        return filters


class UpcomingInstanceFilters(Filters):
    """
    This is utilized for taking in the query parameters related to "filtering" Event entities in Projects list events endpoint.
    """

    @classmethod
    def from_params(cls, params: MultiDict) -> UpcomingInstanceFilters:
        filters = cls._from_params(
            params,
            [
                PROJECT_ID_QUERY_NAME,
                JOURNEY_ID_QUERY_NAME,
                JOURNEY_NAMES_QUERY_NAME,
                START_RANGE_QUERY_NAME,
                END_RANGE_QUERY_NAME,
            ],
        )

        if filters.start_range is None:
            raise ValidationError({START_RANGE_QUERY_NAME: "The start of the range must be set"})
        cls.validate_time_range(filters.start_range, filters.end_range, START_RANGE_QUERY_NAME)
        return filters


@dataclass
class ActionFilters(Filters):
    """
    This is utilized for taking in the query parameters related to filtering Action entities
    """

    @classmethod
    def from_params(cls, params: MultiDict) -> ActionFilters:
        filters = cls._from_params(
            params,
            [
                ACTION_IMPL_QUERY_NAME,
            ],
        )
        cls.validate_action_impls(filters.action_impls)
        return filters
