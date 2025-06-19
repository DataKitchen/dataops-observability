__all__ = ["RunHandler"]

import logging
from typing import cast

from peewee import DoesNotExist

from common.datetime_utils import timestamp_to_datetime
from common.entities import ComponentType, Pipeline, Run, RunStatus
from common.events import EventHandlerBase
from common.events.internal import RunAlert
from common.events.v1 import Event, MessageLogEvent, MetricLogEvent, RunStatusEvent, TestOutcomesEvent
from common.peewee_extensions.fields import UTCTimestampField
from run_manager.context import RunManagerContext
from run_manager.event_handlers.utils import update_state

LOG = logging.getLogger(__name__)


def _start_pending_run(event: Event, run: Run) -> None:
    """Start a pending run"""
    run.key = event.run_key
    run.start_time = cast(UTCTimestampField, event.event_timestamp)
    run.status = RunStatus.RUNNING.name
    LOG.info("Started pending run '%s'", run.id)


class RunHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context
        self.alerts: list[RunAlert] = []

    def handle_message_log(self, event: MessageLogEvent) -> bool:
        self._handle_event(event)
        return True

    def handle_metric_log(self, event: MetricLogEvent) -> bool:
        self._handle_event(event)
        return True

    def handle_run_status(self, event: RunStatusEvent) -> bool:
        if pipeline := self.context.pipeline:
            if (run := self._get_run(event, pipeline)) is None:
                run = self._create_run(event)
                if RunStatus.has_run_started(event.status):
                    self.context.started_run = True
            self.context.run = run

            # If the RunStatusEvent contains expected_start_time metadata AND the expected_start_time is not yet set,
            # apply the expected_start_time to the Run instance.
            if (
                (expected_timestamp := event.metadata.get("expected_start_time", None))
                and isinstance(expected_timestamp, float)
                and getattr(run, "expected_start_time", None) is None
            ):
                timestamp = timestamp_to_datetime(expected_timestamp)
                run.expected_start_time = cast(UTCTimestampField, timestamp)

            if run.status == RunStatus.PENDING.name and RunStatus.has_run_started(event.status):
                _start_pending_run(event, self.context.run)
                self.context.started_run = True
            self._set_run_name(event)

            if event.task_key is None:
                self.context.prev_run_status = run.status
                if not RunStatus.has_run_started(event.status):
                    run.key = None
                    run.start_time = cast(UTCTimestampField, None)
                    run.end_time = cast(UTCTimestampField, None)
                    run.status = event.status
                else:
                    update_state(run, event)

                # If a new run was created it has not yet been inserted to the db, force insert it here
                run.save(force_insert=self.context.created_run)
            else:
                run.save(force_insert=self.context.created_run)
        return True

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        self._handle_event(event)
        return True

    def _handle_event(self, event: Event) -> None:
        if event.component_type == ComponentType.BATCH_PIPELINE and self.context.pipeline:
            if (run := self._get_run(event, self.context.pipeline)) is None:
                run = self._create_run(event)
                self.context.started_run = True

            self.context.run = run

            if (run := self.context.run) is not None:
                if run.status == RunStatus.PENDING.name:
                    _start_pending_run(event, run)
                    self.context.started_run = True
                self._set_run_name(event)
                # If a new run was created it has not yet been inserted to the db, force insert it here
                run.save(force_insert=self.context.created_run)
            else:
                raise ValueError(
                    f"{event.__class__.__name__} {event.event_id} failed to get a create a new run "
                    f"for batch-pipeline {self.context.pipeline.id}"
                )

    def _get_run(self, event: Event, pipeline: Pipeline) -> Run | None:
        """
        Get an existing run instance

        The priorities for finding a run are
        1. Matching run_key
        2. Pending run
        Missing runs are always excluded as they have reached their end state
        """
        try:
            query_filters = Run.status == RunStatus.PENDING.name
            if event.run_key is not None:
                query_filters |= Run.key == event.run_key
            query_filters &= Run.pipeline == pipeline
            run: Run = (
                Run.select()
                .where(query_filters)
                # Order null-keys last in order to prefer existing run matching event.run_key
                .order_by(Run.key.asc(nulls="LAST"))
                .get()
            )
        except DoesNotExist:
            return None
        return run

    def _create_run(self, event: Event) -> Run:
        """Create a Run as well as the RunTasks for the required Tasks associated with the pipeline."""
        run: Run = Run(
            pipeline=self.context.pipeline,
            key=event.run_key,
            start_time=event.event_timestamp,
            status=RunStatus.RUNNING.name,
        )
        self.context.created_run = True
        LOG.info("Created new run '%s' for pipeline '%s'", run.id, getattr(self.context.pipeline, "id"))
        return run

    def _set_run_name(self, event: Event) -> None:
        """Set/Update run name if set in event"""
        if (run := self.context.run) and (new_run_name := event.run_name) and new_run_name != run.name:
            run.name = new_run_name
