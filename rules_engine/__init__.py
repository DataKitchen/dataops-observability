from typing import Union

from common.events.internal import InstanceAlert, RunAlert
from common.events.v1 import Event

EVENT_TYPE = Union[Event, RunAlert, InstanceAlert]
"""All types of events supported by Rule evaluation."""

ALERT_EVENT = Union[RunAlert, InstanceAlert]
"""All internal alert event types."""


__all__ = ("EVENT_TYPE", "ALERT_EVENT")
