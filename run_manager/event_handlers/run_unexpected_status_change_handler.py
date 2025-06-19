import logging

from common.entities import RunAlertType, RunStatus
from common.events import EventHandlerBase
from common.events.internal import RunAlert
from common.events.v1 import MessageLogEvent, MetricLogEvent, RunStatusEvent, TestOutcomesEvent
from run_manager.alerts import create_run_alert
from run_manager.context import RunManagerContext

LOG = logging.getLogger(__name__)

ALERT_TYPES = {
    RunStatus.PENDING.name: RunAlertType.LATE_START,
    RunStatus.MISSING.name: RunAlertType.MISSING_RUN,
    RunStatus.COMPLETED_WITH_WARNINGS.name: RunAlertType.COMPLETED_WITH_WARNINGS,
    RunStatus.FAILED.name: RunAlertType.FAILED,
}
"""Map new run status to alert type"""


def _get_alert_type(context: RunManagerContext) -> RunAlertType | None:
    if context.run is None:
        raise ValueError("The `run` attribute for the context object must be populated with a valid Run instance")

    if context.created_run is False and context.prev_run_status in (
        RunStatus.COMPLETED.name,
        RunStatus.COMPLETED_WITH_WARNINGS.name,
        RunStatus.FAILED.name,
    ):
        # If there is a status update and the old status implies that the run was completed then it ie expected that
        # the run should receive no further updates. If a status update IS received, generate an Alert to indicate
        # the inconsistent behavior.
        return RunAlertType.UNEXPECTED_STATUS_CHANGE
    return ALERT_TYPES.get(context.run.status)


class RunUnexpectedStatusChangeHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context
        self.alerts: list[RunAlert] = []

    def handle_message_log(self, event: MessageLogEvent) -> bool:
        return True

    def handle_metric_log(self, event: MetricLogEvent) -> bool:
        return True

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        return True

    def handle_run_status(self, event: RunStatusEvent) -> bool:
        if (pipeline := self.context.pipeline) is None or (run := self.context.run) is None:
            raise ValueError(
                "The context object must be populated with a valid Pipeline and Run instance for RunStatusEvent"
            )

        if (alert_type := _get_alert_type(self.context)) is not None:
            self.alerts.append(create_run_alert(alert_type, run, pipeline))
        return True
