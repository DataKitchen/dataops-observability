__all__ = ["WebhookAction"]

import logging
from typing import Any, Union
from collections.abc import Mapping
from uuid import UUID

from requests_extensions import get_session

from common.entities import Rule
from common.events.internal import InstanceAlert, RunAlert, AgentStatusChangeEvent
from common.events.v1 import Event
from rules_engine.typing import EVENT_TYPE
from common.actions.action import ActionResult, BaseAction
from common.actions.data_points import AlertDataPoints, DataPoints, AgentStatusChangeDataPoints

LOG = logging.getLogger(__name__)


def format_data(data: Union[None, list, dict, str], data_points: Mapping) -> Any:
    """
    Format strings found in data structure with the given data points

    The function recursively iterates the given data structure to find strings
    to format using Python's str.format function. It returns a formatted copy
    of data
    """
    # Recursion depth error is caught by _run()
    if isinstance(data, list):
        return [format_data(v, data_points) for v in data]
    elif isinstance(data, dict):
        return {k: format_data(v, data_points) for k, v in data.items()}
    elif isinstance(data, str):
        try:
            return data.format(**data_points)
        except (ValueError, AttributeError, KeyError):
            LOG.warning("User supplied string could not be formatted", exc_info=True)
            # Prioritize action execution by suppressing formatting errors
            return data
    else:
        return data


class WebhookAction(BaseAction):
    required_arguments = {"url", "method"}

    def _run(self, event: EVENT_TYPE, rule: Rule, _: UUID | None) -> ActionResult:
        data_points: Mapping
        match event:
            case RunAlert() | InstanceAlert():
                data_points = AlertDataPoints(event, rule)
            case AgentStatusChangeEvent():
                data_points = AgentStatusChangeDataPoints(event, rule)
            case Event():
                data_points = DataPoints(event, rule)
            case _:
                data_points = {}  # type: ignore[unreachable]
        try:
            response = get_session().request(
                self.arguments["method"],
                format_data(self.arguments["url"], data_points),
                headers=self._parse_headers(data_points),
                json=format_data(self.arguments.get("payload"), data_points),
            )
            response.raise_for_status()
        except Exception as e:
            return ActionResult(False, None, e)
        return ActionResult(True, {"status_code": response.status_code}, None)

    def _parse_headers(self, data_points: Mapping) -> dict[str, str] | None:
        if headers := self.arguments.get("headers"):
            return {h["key"]: format_data(h["value"], data_points) for h in headers}
        else:
            return None
