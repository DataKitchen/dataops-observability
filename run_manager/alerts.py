import logging
from collections.abc import Iterable
from uuid import UUID

from peewee import chunked

from common.constants import BATCH_SIZE
from common.entities import (
    AlertLevel,
    Component,
    Instance,
    InstanceAlert,
    InstanceAlertType,
    InstanceSet,
    InstancesInstanceSets,
    Pipeline,
    Run,
    RunAlert,
    RunAlertType,
)
from common.entities.alert import InstanceAlertsComponents
from common.events.internal import InstanceAlert as InstanceAlertEvent
from common.events.internal import RunAlert as RunAlertEvent
from common.user_strings.alert_descriptions import INSTANCE_ALERT_DESCRIPTIONS, RUN_ALERT_DESCRIPTIONS

RUN_ALERT_LEVELS = {
    RunAlertType.LATE_END: AlertLevel.WARNING,
    RunAlertType.LATE_START: AlertLevel.WARNING,
    RunAlertType.MISSING_RUN: AlertLevel.ERROR,
    RunAlertType.COMPLETED_WITH_WARNINGS: AlertLevel.WARNING,
    RunAlertType.FAILED: AlertLevel.ERROR,
    RunAlertType.UNEXPECTED_STATUS_CHANGE: AlertLevel.WARNING,
}
"""Map a Run Alert type to an alert level."""

INSTANCE_ALERT_LEVELS = {
    InstanceAlertType.DATASET_NOT_READY: AlertLevel.WARNING,
    InstanceAlertType.INCOMPLETE: AlertLevel.ERROR,
    InstanceAlertType.OUT_OF_SEQUENCE: AlertLevel.ERROR,
    InstanceAlertType.TESTS_HAD_WARNINGS: AlertLevel.WARNING,
    InstanceAlertType.TESTS_FAILED: AlertLevel.ERROR,
}
"""Map an Instance Alert type to an alert level."""

LOG = logging.getLogger(__name__)


def create_run_alert(alert_type: RunAlertType, run: Run, pipeline: Pipeline) -> RunAlertEvent:
    alert_level = RUN_ALERT_LEVELS[alert_type]
    alert_description = RUN_ALERT_DESCRIPTIONS[alert_type].format(name=pipeline.display_name)
    alert = RunAlert(run=run, level=alert_level, type=alert_type, description=alert_description)

    if alert_type in (RunAlertType.LATE_END, RunAlertType.LATE_START, RunAlertType.MISSING_RUN):
        # Use the attribute settrs for expected start/end time (they are not columns in the database)
        if end_dt := run.expected_end_time:
            alert.expected_end_time = end_dt
        if start_dt := run.expected_start_time:
            alert.expected_start_time = start_dt
    alert.save(force_insert=True)
    instances = (
        Instance.select(Instance.id).join(InstancesInstanceSets).join(InstanceSet).join(Run).where(Run.id == run.id)
    )
    (
        Instance.update(
            has_errors=Instance.has_errors if alert_level != AlertLevel.ERROR else True,
            has_warnings=Instance.has_warnings if alert_level != AlertLevel.WARNING else True,
        ).where(Instance.id.in_([i.id for i in instances]))
    ).execute()
    return RunAlertEvent(
        project_id=pipeline.project_id,
        level=alert_level,
        type=alert_type,
        description=alert_description,
        alert_id=alert.id,
        run_id=run.id,
        batch_pipeline_id=pipeline.id,
        created_timestamp=alert.created_on,
    )


def create_instance_alert(
    alert_type: InstanceAlertType,
    instance: Instance,
    component: Component | None = None,
    alert_components: Iterable[UUID] | None = None,
) -> InstanceAlertEvent:
    alert_level = INSTANCE_ALERT_LEVELS[alert_type]
    alert_description = INSTANCE_ALERT_DESCRIPTIONS[alert_type].format(
        component_type=component.display_type if component else "N/A",
        component_name=component.display_name if component else "N/A",
    )
    alert = InstanceAlert.create(
        instance=instance,
        level=alert_level.name,
        type=alert_type.name,
        description=alert_description,
    )
    alert_components = alert_components or []
    alert_components = [
        InstanceAlertsComponents(instance_alert=alert.id, component=component) for component in alert_components
    ]
    InstanceAlertsComponents.bulk_create(alert_components, batch_size=BATCH_SIZE)

    if alert_level == AlertLevel.WARNING and not instance.has_warnings:
        Instance.update({Instance.has_warnings: True}).where(Instance.id == instance.id).execute()
    if alert_level == AlertLevel.ERROR and not instance.has_errors:
        Instance.update({Instance.has_errors: True}).where(Instance.id == instance.id).execute()

    LOG.info("%s [%s] created for %s", alert, alert_type, instance)
    return InstanceAlertEvent(
        project_id=instance.journey.project_id,
        level=alert_level,
        type=alert_type,
        description=alert_description,
        alert_id=alert.id,
        instance_id=instance.id,
        journey_id=instance.journey_id,
        created_timestamp=alert.created_on,
    )


def update_instances_alert_components(update_list: list[tuple[UUID, UUID]]) -> None:
    for batch in chunked(update_list, BATCH_SIZE):
        InstanceAlertsComponents.insert_many(
            batch, fields=[InstanceAlertsComponents.instance_alert, InstanceAlertsComponents.component]
        ).on_conflict_ignore().execute()
