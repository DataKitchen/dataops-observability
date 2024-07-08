import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Callable, Iterator, Optional, cast
from uuid import UUID

from peewee import DoesNotExist

from common.datetime_utils import datetime_formatted, datetime_iso8601
from common.entities import Rule
from common.entity_services import ProjectService
from common.entity_services.helpers import ListRules
from common.events.internal import RunAlert, AgentStatusChangeEvent
from common.events.v1 import Event
from rules_engine.typing import ALERT_EVENT, EVENT_TYPE

LOG = logging.getLogger(__name__)


class NamespacedDataPointsBase:
    mappings: dict[str, Callable]

    def __getattr__(self, attr: str) -> Any:
        if f := self.mappings.get(attr):
            try:
                return f()
            except Exception as e:
                raise AttributeError(f"Error when fetching data point '{attr}'") from e
        else:
            raise AttributeError(f"'{attr}' is not a valid data point")


class DatetimeDataPoints(NamespacedDataPointsBase):
    def __init__(self, value: datetime):
        self.mappings = {
            "human": lambda: datetime_formatted(value),
            "iso": lambda: datetime_iso8601(value),
        }


class EventDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: Event):
        self.event = event
        self.mappings = {
            "id": self._id,
            "external_url": self._external_url,
            "log_level": self._log_level,
            "message": self._message,
            "metric_key": self._metric_key,
            "metric_value": self._metric_value,
            "event_timestamp": self._event_timestamp,
            "event_timestamp_formatted": self._event_timestamp_formatted,
            "received_timestamp": self._received_timestamp,
            "received_timestamp_formatted": self._received_timestamp_formatted,
        }

    def _id(self) -> UUID:
        return self.event.event_id

    # external_url has a fallback value because it's an optional field whereas
    # log_level, message etc are required for the event type
    def _external_url(self) -> str:
        if external_url := self.event.external_url:
            return external_url
        return "N/A"

    # As log_level, message etc are not available on all event types, getattr
    # is used to please mypy
    def _log_level(self) -> str:
        ret: str = getattr(self.event, "log_level")
        return ret

    def _message(self) -> str:
        ret: str = getattr(self.event, "message")
        return ret

    def _metric_key(self) -> str:
        ret: str = getattr(self.event, "metric_key")
        return ret

    def _metric_value(self) -> int:
        ret: int = getattr(self.event, "metric_value")
        return ret

    def _event_timestamp(self) -> str:
        return datetime_iso8601(self.event.event_timestamp)

    def _event_timestamp_formatted(self) -> str:
        return datetime_formatted(self.event.event_timestamp)

    def _received_timestamp(self) -> str:
        return datetime_iso8601(self.event.received_timestamp)

    def _received_timestamp_formatted(self) -> str:
        return datetime_formatted(self.event.received_timestamp)


class ProjectDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: EVENT_TYPE):
        self.event = event
        self.mappings = {
            "id": self._id,
            "name": self._name,
        }

    def _id(self) -> Optional[UUID]:
        return self.event.project_id

    def _name(self) -> str:
        ret: str = self.event.project.name
        return ret


class ComponentDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: Event):
        self.event = event
        self.mappings = {
            "id": self._id,
            "key": self._key,
            "name": self._name,
            "type": self._type,
        }

    def _id(self) -> Optional[UUID]:
        return self.event.component_id

    def _key(self) -> Optional[str]:
        return self.event.component_key

    def _name(self) -> Optional[str]:
        return self.event.component.display_name

    def _type(self) -> Optional[str]:
        return self.event.component_type.name


class PipelineDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: Event):
        self.event = event
        self.mappings = {
            "id": self._id,
            "key": self._key,
            "name": self._name,
        }

    def _id(self) -> Optional[UUID]:
        return self.event.pipeline_id

    def _key(self) -> Optional[str]:
        return self.event.pipeline_key

    def _name(self) -> Optional[str]:
        return cast(str, self.event.pipeline.display_name)


class RunDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: Event):
        self.event = event
        self.mappings = {
            "id": self._id,
            "key": self._key,
            "name": self._name,
            "status": self._status,
            "start_time": self._start_time,
            "start_time_formatted": self._start_time_formatted,
            "expected_start_time": self._expected_start_time,
            "expected_start_time_formatted": self._expected_start_time_formatted,
            "end_time": self._end_time,
            "end_time_formatted": self._end_time_formatted,
            "expected_end_time": self._expected_end_time,
            "expected_end_time_formatted": self._expected_end_time_formatted,
        }

    def _id(self) -> Optional[UUID]:
        return self.event.run_id

    def _key(self) -> Optional[str]:
        return self.event.run_key

    def _name(self) -> Optional[str]:
        return self.event.run_name

    def _status(self) -> str:
        ret: str = self.event.run.status
        return ret

    def _start_time(self) -> str:
        if run := getattr(self.event, "run", None):
            if start_time := getattr(run, "start_time", None):
                return datetime_iso8601(start_time)
        return "N/A"

    def _start_time_formatted(self) -> str:
        if run := getattr(self.event, "run", None):
            if start_time := getattr(run, "start_time", None):
                return datetime_formatted(start_time)
        return "N/A"

    def _expected_start_dt(self) -> Optional[datetime]:
        try:
            run = getattr(self.event, "run", None)
        except DoesNotExist:
            return None
        else:
            if run:
                if expected_start_time := getattr(run, "expected_start_time", None):
                    return cast(datetime, expected_start_time)
        return None

    def _expected_start_time(self) -> Optional[str]:
        val = self._expected_start_dt()
        return datetime_iso8601(val) if val else None

    def _expected_start_time_formatted(self) -> Optional[str]:
        val = self._expected_start_dt()
        return datetime_formatted(val) if val else None

    def _end_time(self) -> str:
        if run := getattr(self.event, "run", None):
            if end_time := getattr(run, "end_time", None):
                return datetime_iso8601(end_time)
        return "N/A"

    def _end_time_formatted(self) -> str:
        if run := getattr(self.event, "run", None):
            if end_time := getattr(run, "end_time", None):
                return datetime_formatted(end_time)
        return "N/A"

    def _expected_end_dt(self) -> Optional[datetime]:
        try:
            run = getattr(self.event, "run", None)
        except DoesNotExist:
            return None
        else:
            if run:
                if expected_end_time := getattr(run, "expected_end_time", None):
                    return cast(datetime, expected_end_time)
        return None

    def _expected_end_time(self) -> Optional[str]:
        val = self._expected_end_dt()
        return datetime_iso8601(val) if val else None

    def _expected_end_time_formatted(self) -> Optional[str]:
        val = self._expected_end_dt()
        return datetime_formatted(val) if val else None


class TaskDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: Event):
        self.event = event
        self.mappings = {
            "id": self._id,
            "key": self._key,
            "name": self._name,
        }

    def _id(self) -> Optional[UUID]:
        return self.event.task_id

    def _key(self) -> Optional[str]:
        ret: str = getattr(self.event, "task_key")
        return ret

    def _name(self) -> str:
        return self.event.task.display_name


class RunTaskDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: Event) -> None:
        self.event = event
        self.mappings = {
            "id": self._id,
            "status": self._status,
            "start_time": self._start_time,
            "start_time_formatted": self._start_time_formatted,
            "end_time": self._end_time,
            "end_time_formatted": self._end_time_formatted,
        }

    def _id(self) -> Optional[UUID]:
        return self.event.run_task_id

    def _status(self) -> str:
        ret: str = self.event.run_task.status
        return ret

    def _start_time(self) -> str:
        if run_task := getattr(self.event, "run_task", None):
            if start_time := getattr(run_task, "start_time", None):
                return datetime_iso8601(start_time)
        return "N/A"

    def _start_time_formatted(self) -> str:
        if run_task := getattr(self.event, "run_task", None):
            if start_time := getattr(run_task, "start_time", None):
                return datetime_formatted(start_time)
        return "N/A"

    def _end_time(self) -> str:
        if run_task := getattr(self.event, "run_task", None):
            if end_time := getattr(run_task, "end_time", None):
                return datetime_iso8601(end_time)
        return "N/A"

    def _end_time_formatted(self) -> str:
        if run_task := getattr(self.event, "run_task", None):
            if end_time := getattr(run_task, "end_time", None):
                return datetime_formatted(end_time)
        return "N/A"


class CompanyDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: EVENT_TYPE) -> None:
        self.event = event
        self.mappings = {
            "ui_url": self._ui_url,
        }

    def _ui_url(self) -> str:
        # Multiple auth providers is not something we support atm so we can assume to take the first one
        page = ProjectService.get_auth_providers_with_rules(str(self.event.project_id), ListRules(count=1))
        ret: str = page.results[0].domain
        return ret


class BaseDataPoints(Mapping):
    def __init__(self, event: EVENT_TYPE, rule: Rule):
        self.namespaces = self.get_namespaces(event, rule)

    def __getattr__(self, attr: str) -> Any:
        return self.namespaces[attr]

    def __getitem__(self, key: str) -> Any:
        return self.namespaces[key]

    def __iter__(self) -> Iterator:
        yield from self.namespaces

    def __len__(self) -> int:
        return len(self.namespaces)

    def get_namespaces(self, event: EVENT_TYPE, rule: Rule) -> dict[str, NamespacedDataPointsBase]:
        return {
            "company": CompanyDataPoints(event),
            "project": ProjectDataPoints(event),
        }


class DataPoints(BaseDataPoints):
    def get_namespaces(self, event: EVENT_TYPE, rule: Rule) -> dict[str, NamespacedDataPointsBase]:
        event = cast(Event, event)
        return {
            **super().get_namespaces(event, rule),
            "component": ComponentDataPoints(event),
            "event": EventDataPoints(event),
            "pipeline": ComponentDataPoints(event),
            "rule": RuleDataPoints(rule),
            "run": RunDataPoints(event),
            "run_task": RunTaskDataPoints(event),
            "task": TaskDataPoints(event),
        }


class InternalEventDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: ALERT_EVENT) -> None:
        self.event = event
        self.mappings = {
            "id": self._id,
            "event_timestamp": self._event_timestamp,
            "event_timestamp_formatted": self._event_timestamp_formatted,
        }

    def _id(self) -> UUID:
        return self.event.event_id

    def _event_timestamp(self) -> str:
        return datetime_iso8601(self.event.created_timestamp)

    def _event_timestamp_formatted(self) -> str:
        return datetime_formatted(self.event.created_timestamp)


class AlertEventDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: ALERT_EVENT) -> None:
        self.event = event
        self.mappings = {
            "level": self._alert_level,
            "type": self._alert_type,
            "expected_start_time_formatted": self._expected_start_time_formatted,
            "expected_end_time_formatted": self._expected_end_time_formatted,
        }

    def _alert_level(self) -> str:
        level: str = self.event.level.value
        return level

    def _alert_type(self) -> str:
        _type: str = self.event.type.value
        return _type

    def _expected_start_dt(self) -> Optional[datetime]:
        try:
            alert = getattr(self.event, "alert", None)
        except DoesNotExist:
            return None
        else:
            if alert:
                if expected_start_time := getattr(alert, "expected_start_time", None):
                    return cast(datetime, expected_start_time)
        return None

    def _expected_end_dt(self) -> Optional[datetime]:
        try:
            alert = getattr(self.event, "alert", None)
        except DoesNotExist:
            return None
        else:
            if alert:
                if expected_end_time := getattr(alert, "expected_end_time", None):
                    return cast(datetime, expected_end_time)
        return None

    def _expected_start_time_formatted(self) -> Optional[str]:
        val = self._expected_start_dt()
        return datetime_formatted(val) if val else None

    def _expected_end_time_formatted(self) -> Optional[str]:
        val = self._expected_end_dt()
        return datetime_formatted(val) if val else None


class InternalComponentDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: RunAlert) -> None:
        self.event = event
        self.mappings = {
            "id": self._id,
            "key": self._key,
            "name": self._name,
        }

    def _id(self) -> Optional[UUID]:
        id: Optional[UUID] = self.event.batch_pipeline_id
        return id

    def _key(self) -> Optional[str]:
        key: Optional[str] = self.event.batch_pipeline.key
        return key

    def _name(self) -> Optional[str]:
        name: Optional[str] = self.event.batch_pipeline.display_name
        return name


class RunAlertDatapoints(NamespacedDataPointsBase):
    def __init__(self, event: RunAlert) -> None:
        self.event = event
        self.mappings = {
            "id": self._id,
            "key": self._key,
            "name": self._name,
        }

    def _id(self) -> Optional[UUID]:
        id: Optional[UUID] = self.event.run.id
        return id

    def _key(self) -> Optional[str]:
        key: Optional[str] = self.event.run.key
        return key

    def _name(self) -> Optional[str]:
        name: Optional[str] = self.event.run.name
        return name


class RuleDataPoints(NamespacedDataPointsBase):
    def __init__(self, rule: Rule) -> None:
        self.rule = rule
        self.mappings = {
            "run_state_matches": self._run_state_matches,
            "run_state_count": self._run_state_count,
            "run_state_group_run_name": self._run_state_group_run_name,
            "run_state_trigger_successive": self._run_state_trigger_successive,
        }

    def _run_state_matches(self) -> Optional[str]:
        try:
            matches: Optional[str] = self.rule.rule_data["conditions"][0]["run_state"]["matches"]
            return matches
        except Exception:
            return None

    def _run_state_count(self) -> Optional[str]:
        try:
            return str(self.rule.rule_data["conditions"][0]["run_state"]["count"])
        except Exception:
            return None

    def _run_state_group_run_name(self) -> Optional[str]:
        try:
            return str(self.rule.rule_data["conditions"][0]["run_state"]["group_run_name"])
        except Exception:
            return None

    def _run_state_trigger_successive(self) -> Optional[str]:
        try:
            return str(self.rule.rule_data["conditions"][0]["run_state"]["trigger_successive"])
        except Exception:
            return None


class AlertDataPoints(DataPoints):
    def get_namespaces(self, event: EVENT_TYPE, rule: Rule) -> dict[str, NamespacedDataPointsBase]:
        event = cast(ALERT_EVENT, event)
        namespaces = {
            **super().get_namespaces(event, rule),
            "alert": AlertEventDataPoints(event),
            "event": InternalEventDataPoints(event),
        }
        if isinstance(event, RunAlert):
            namespaces["component"] = InternalComponentDataPoints(event)
            namespaces["run"] = RunAlertDatapoints(event)

        return namespaces


class AgentDataPoints(NamespacedDataPointsBase):
    def __init__(self, event: AgentStatusChangeEvent) -> None:
        self.event = event
        self.mappings = {
            "key": lambda: event.agent_key,
            "tool": lambda: event.agent_tool,
            "latest_heartbeat": lambda: DatetimeDataPoints(event.latest_heartbeat),
            "latest_event_timestamp": lambda: DatetimeDataPoints(event.latest_event_timestamp),
        }


class AgentStatusChangeDataPoints(BaseDataPoints):
    def get_namespaces(self, event: EVENT_TYPE, rule: Rule) -> dict[str, NamespacedDataPointsBase]:
        namespaces = super().get_namespaces(event, rule)
        match event:
            case AgentStatusChangeEvent():
                namespaces["agent"] = AgentDataPoints(event)
        return namespaces
