from __future__ import annotations

import copy
import logging
import os
import re
import time
from argparse import Action, ArgumentParser, Namespace
from datetime import datetime
from typing import Any, Optional, Sequence, Type, Union

from requests_extensions import get_session

from cli.base import ScriptBase
from common.api.flask_ext.authentication import ServiceAccountAuth

SA_KEY_ENV_NAME = "OBSERVABILITY_SERVICE_ACCOUNT_KEY"

from common.events.v1 import EVENT_TYPE_MAP

LOG = logging.getLogger(__name__)

send_events = []


class BaseEvent:
    base_endpoint = "events/v1"
    base_data = {
        "pipeline_key": None,
        "run_key": "a run key",
        "event_timestamp": None,
    }
    endpoint = ""
    additional_data: dict[str, str] = {}

    def __init__(self, values: dict[str, Any], remove: list[str]) -> None:
        self.values = values
        self.remove = remove

    def get_data(self, pipeline: str) -> dict[str, Any]:
        data = copy.deepcopy(self.base_data)
        data["event_timestamp"] = str(datetime.utcnow())
        data["pipeline_key"] = pipeline
        data.update(self.additional_data)
        data.update(self.values)
        for r in self.remove:
            data.pop(r, None)
        return data


class MessageLogEvent(BaseEvent):
    event_type = EVENT_TYPE_MAP["MessageLogEvent"]
    endpoint = "message-log"
    additional_data: dict[str, str] = {"message": "a log message", "log_level": "INFO"}


class MetricLogEvent(BaseEvent):
    event_type = EVENT_TYPE_MAP["MetricLogEvent"]
    endpoint = "metric-log"
    additional_data = {"metric_key": "a key", "metric_value": "10"}


class TestOutcomesEvent(BaseEvent):
    event_type = EVENT_TYPE_MAP["TestOutcomesEvent"]
    endpoint = "test-outcomes"
    # TODO: Customize test_outcomes
    additional_data: dict[str, Any] = {
        "test_outcomes": [{"name": "test name", "status": "PASSED"}],
    }


class RunStatusEvent(BaseEvent):
    event_type = EVENT_TYPE_MAP["RunStatusEvent"]
    endpoint = "run-status"
    additional_data = {"status": "RUNNING"}


EVENTS_MAP = {
    "message": MessageLogEvent,
    "metric": MetricLogEvent,
    "testoutcomes": TestOutcomesEvent,
    "runstatus": RunStatusEvent,
}


def make_events_action(event_id: str) -> Type[Action]:
    class EventsAction(Action):
        def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            event_data = {}
            remove_fields = []
            # Parse event field data
            for v in values or []:
                if m := re.match(r"([^=]+)(?:=(.*))?", v):
                    if m.group(2) is None:
                        remove_fields.append(m.group(1))
                    else:
                        event_data[m.group(1)] = m.group(2)
            send_events.append(EVENTS_MAP[event_id](event_data, remove_fields))

    return EventsAction


class GenEvent(ScriptBase):
    """Generate event to the Event API"""

    subcommand: str = "events"
    session = get_session()

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Send events to the Event API"
        parser.usage = """$ cli events [URL] [PIPELINE] [SA KEY] [EVENTS...]

        Send events to the Event API. Each event type has default data for each
        required field. Non-required fields are unset by default.

        Examples of event field customizations:
        Set value       - status=RUNNING
        Set empty value - status=
        Remove field    - status

        Each event type may be used any number of times. The event will be sent
        in the order the flags are given.

        By default the project_id will be set to the most recent project added
        to the database. This will change when SA keys are introduced.

        Examples:
        # Send three events - log message, test outcomes and status event
        cli events <base URL> <SA key> <pipeline> --log --testoutcomes --status

        # Send two metric messages
        cli events <base URL> <SA key> <pipeline> --metric --metric

        # Send two run statuses
        cli events <base URL> <SA key> <pipeline> --runstatus status=RUNNING --runstatus status=COMPLETED
        """
        parser.add_argument("URL", nargs=1, help="event API URL e.g. 'http://localhost:5001'")
        parser.add_argument(
            "PIPELINE_NAME",
            nargs=1,
            help="pipline to use for all events, may be overridden for individual events with 'pipeline_key=<name>'",
        )
        parser.add_argument(
            "SA KEY", nargs="?", help=f"Service account key, or use environment variable {SA_KEY_ENV_NAME}"
        )
        parser.add_argument("-d", "--delay", nargs=1, type=float, help="Delay between sent events")

        event_parser = parser.add_argument_group(title="Events")
        event_parser.description = "Event types to send"
        for name, klass in EVENTS_MAP.items():
            event_parser.add_argument(
                f"--{name}",
                dest="FIELD DATA",
                nargs="*",
                action=make_events_action(name),
                help=f"send {klass.__name__}",
            )

    def subcmd_entry_point(self) -> None:
        self.url = self.kwargs["URL"][0]
        self.pipeline = self.kwargs["PIPELINE_NAME"][0]
        self.key = self.kwargs["SA KEY"] if self.kwargs["SA KEY"] else os.environ.get(SA_KEY_ENV_NAME)
        if self.kwargs["delay"] is None:
            delay = 0
        else:
            delay = self.kwargs["delay"][0]

        for i, event in enumerate(send_events):
            if delay is not None and i != 0:
                LOG.debug("Sleeping for %s seconds", delay)
                time.sleep(delay)
            self.post_event(event)

    def post_event(self, event: BaseEvent) -> None:
        event_name = event.__class__.__name__
        headers = {
            "Content-Type": "application/json",
            ServiceAccountAuth.header_name: self.key,
        }
        event_data = event.get_data(self.pipeline)
        LOG.debug("Sending %s: %s", event_name, event_data)
        response = self.session.post(
            f"{self.url}/{event.base_endpoint}/{event.endpoint}", headers=headers, json=event_data
        )
        if response.ok:
            LOG.info("%s sent #g<OK>", event_name)
        else:
            LOG.error("%s #r<response %s>: %s", event_name, response.status_code, response.text)
