import logging
from collections import namedtuple
from uuid import uuid4

from peewee import PREFETCH_TYPE, Case

from common.datetime_utils import datetime_to_timestamp
from common.entities import Component, InstanceAlertType, Pipeline, Run, RunAlert, RunAlertType, RunStatus
from common.entities.dataset_operation import DatasetOperation, DatasetOperationType
from common.entities.event import EventVersion
from common.entity_services import ComponentService
from common.events.enums import EventSources, ScheduleType
from common.events.internal import InstanceAlert as InstanceAlertEvent
from common.events.internal import RunAlert as RunAlertEvent
from common.events.internal import ScheduledEvent
from common.events.v1 import RunStatusEvent
from run_manager.alerts import create_instance_alert, create_run_alert

LOG = logging.getLogger(__name__)

# TODO: When we publish internally generated run statuses, these
# could be a single list that should be handled in a generic way
Events = namedtuple("Events", ("run_statuses", "alerts"))


def _handle_batch_start(event: ScheduledEvent) -> Events:
    run_statuses = []
    runs = (
        Run.select(Run, Component)
        .join(Component, on=(Component.id == Run.pipeline))
        .where(Component.id == event.component_id, Run.status == RunStatus.PENDING.name)
    )
    for run in runs:
        run_statuses.append(
            RunStatusEvent(
                status=RunStatus.MISSING.name,
                pipeline_id=event.component_id,
                source=EventSources.SCHEDULER.name,
                event_timestamp=event.schedule_timestamp,
                received_timestamp=event.schedule_timestamp,
                run_id=run.id,
                event_id=uuid4(),
                version=EventVersion.V1,
                pipeline_key=None,
                run_key=None,
                run_name=None,
                metadata={},
                event_type=RunStatusEvent.__name__,
                component_tool=None,
                project_id=None,
                task_id=None,
                task_name=None,
                task_key=None,
                run_task_id=None,
                external_url=None,
                pipeline_name=None,
                instances=[],
                dataset_id=None,
                dataset_key=None,
                dataset_name=None,
                server_id=None,
                server_key=None,
                server_name=None,
                stream_id=None,
                stream_key=None,
                stream_name=None,
                payload_keys=[],
            )
        )
    return Events(run_statuses, [])


def _handle_batch_start_margin(event: ScheduledEvent) -> Events:
    if event.schedule_margin is None:
        raise ValueError(f"Schedule event with type {event.schedule_type} does not have a schedule_margin")
    runs = (
        Run.select()
        .join(Component, on=(Component.id == Run.pipeline))
        .where(
            Component.id == event.component_id,
            Run.start_time >= event.schedule_timestamp,
            Run.start_time < event.schedule_margin,
        )
    )
    if runs.count() == 0:
        run_status = RunStatusEvent(
            status=RunStatus.PENDING.name,
            pipeline_id=event.component_id,
            source=EventSources.SCHEDULER.name,
            event_timestamp=event.schedule_margin,
            received_timestamp=event.schedule_margin,
            event_id=uuid4(),
            pipeline_key=None,
            run_key=None,
            run_name=None,
            metadata={"expected_start_time": datetime_to_timestamp(event.schedule_timestamp)},
            event_type=RunStatusEvent.__name__,
            version=EventVersion.V1,
            component_tool=None,
            project_id=None,
            run_id=None,
            task_id=None,
            task_name=None,
            task_key=None,
            run_task_id=None,
            external_url=None,
            pipeline_name=None,
            instances=[],
            dataset_id=None,
            dataset_key=None,
            dataset_name=None,
            server_id=None,
            server_key=None,
            server_name=None,
            stream_id=None,
            stream_key=None,
            stream_name=None,
            payload_keys=[],
        )
        return Events([run_status], [])
    else:
        updated_runs = []
        for run in runs:
            if run.expected_start_time is None:
                run.expected_start_time = event.schedule_timestamp
                updated_runs.append(run)
        if updated_runs:
            Run.bulk_update(updated_runs, fields=[Run.expected_start_time])
    return Events([], [])


def _handle_batch_end(event: ScheduledEvent) -> Events:
    late_end = RunAlertType.LATE_END
    rq = (
        Run.select(Run, Pipeline)
        .join(Pipeline)
        .where(
            Pipeline.id == event.component_id,
            Run.status != RunStatus.MISSING.name,
            (Run.end_time.is_null(True)) | (Run.end_time >= event.schedule_timestamp),
        )
        # Pending runs are considered first, after that the most recent start time. Missed runs are ignored.
        .order_by(Case(Run.status, ((RunStatus.PENDING.name, 0),), 1).asc(), Run.start_time.desc(nulls="LAST"))
        .limit(1)
    )
    runs = rq.prefetch(RunAlert.select().where(RunAlert.type == late_end.name), prefetch_type=PREFETCH_TYPE.JOIN)
    for run in runs:
        run.expected_end_time = event.schedule_timestamp
    if len(runs):
        Run.bulk_update(runs, fields=[Run.expected_end_time])

    # Do not add late end alert if the run already has such an alert
    alerts: list[RunAlertEvent] = []
    if (run := runs[0] if len(runs) > 0 else None) is not None and len(run.run_alerts) == 0:
        alerts.append(create_run_alert(late_end, run, run.pipeline))
        LOG.info("Run '%s' ended late", run.id)

    # else: no run, nothing to do
    return Events([], alerts)


def _handle_dataset_arrival_margin(event: ScheduledEvent) -> Events:
    if event.schedule_margin is None:
        raise ValueError(f"Schedule event with type {event.schedule_type} does not have a schedule_margin")

    operation_query = DatasetOperation.select().where(
        DatasetOperation.dataset == event.component_id,
        DatasetOperation.operation_time >= event.schedule_timestamp,
        DatasetOperation.operation_time < event.schedule_margin,
        DatasetOperation.operation == DatasetOperationType.WRITE,
    )

    try:
        operation = operation_query.get()
    except DatasetOperation.DoesNotExist:
        operation = None
    else:
        LOG.info(
            "Found %s within %s - %s interval at %s",
            operation,
            event.schedule_timestamp.time(),
            event.schedule_margin.time(),
            operation.operation_time.time(),
        )

    alerts: list[InstanceAlertEvent] = []
    if operation is None:
        component = Component.get(Component.id == event.component_id)
        LOG.info(
            "%s was supposed to have arrived (written) between %s and %s, creating alerts",
            component,
            event.schedule_timestamp.time(),
            event.schedule_margin.time(),
        )
        for created, instance in ComponentService.get_or_create_active_instances(component):
            if created:
                LOG.info("%s has been created", instance)
            alerts.append(create_instance_alert(InstanceAlertType.DATASET_NOT_READY, instance, component))
    return Events([], alerts)


SCHEDULE_TYPE_HANDLERS = {
    ScheduleType.BATCH_START_TIME: _handle_batch_start,
    ScheduleType.BATCH_START_TIME_MARGIN: _handle_batch_start_margin,
    ScheduleType.BATCH_END_TIME: _handle_batch_end,
    ScheduleType.DATASET_ARRIVAL_MARGIN: _handle_dataset_arrival_margin,
}
"""Mapping of schedule type to handler function"""


def handle_schedule_event(event: ScheduledEvent) -> Events:
    return SCHEDULE_TYPE_HANDLERS[event.schedule_type](event)
