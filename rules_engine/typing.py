__all__ = ("EVENT_TYPE", "ALERT_EVENT", "PROJECT_EVENT", "Rule")

from typing import Union, Protocol

from common.events.internal import InstanceAlert, RunAlert, AgentStatusChangeEvent
from common.events.v1 import Event

EVENT_TYPE = Union[Event, RunAlert, InstanceAlert, AgentStatusChangeEvent]
"""All types of events supported by Rule evaluation."""

ALERT_EVENT = Union[RunAlert, InstanceAlert]
"""All internal alert event types."""

PROJECT_EVENT = AgentStatusChangeEvent
"""All internal events that are attached to a project."""


class Rule(Protocol):
    """The minimal interface a rule has to implement."""

    def evaluate(self, event: EVENT_TYPE) -> None: ...
