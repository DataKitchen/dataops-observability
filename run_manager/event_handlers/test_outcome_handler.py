__all__ = ["TestOutcomeHandler"]

import logging
from typing import cast
from uuid import UUID

from common.entities import ComponentType, Instance, InstanceAlert, InstanceAlertsComponents, InstanceAlertType, Journey
from common.entity_services.test_outcome_service import TestOutcomeService
from common.events import EventHandlerBase
from common.events.internal import InstanceAlert as InstanceAlertEvent
from common.events.v1 import TestOutcomesEvent, TestStatuses
from run_manager.alerts import create_instance_alert
from run_manager.context import RunManagerContext

LOG = logging.getLogger(__name__)

ALERT_TYPE_PER_STATUS: dict[str, InstanceAlertType] = {
    TestStatuses.WARNING.name: InstanceAlertType.TESTS_HAD_WARNINGS,
    TestStatuses.FAILED.name: InstanceAlertType.TESTS_FAILED,
}


class TestOutcomeHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context
        self.alerts: list[InstanceAlertEvent] = []

    def create_instance_alerts(self, event: TestOutcomesEvent) -> None:
        alert_types = {
            ALERT_TYPE_PER_STATUS[oc.status] for oc in event.test_outcomes if oc.status in ALERT_TYPE_PER_STATUS
        }

        if not alert_types:
            return

        skip_alerts = (
            InstanceAlert.select(InstanceAlert.instance, InstanceAlert.type)
            .distinct()
            .join(InstanceAlertsComponents)
            .where(
                InstanceAlert.instance << self.context.instance_ids,
                InstanceAlert.type << alert_types,
                InstanceAlertsComponents.component == event.component_id,
            )
            .tuples()
        )

        create_alerts = {
            instance_id: [alert_type for alert_type in alert_types if (instance_id, alert_type) not in skip_alerts]
            for instance_id in self.context.instance_ids
        }

        if not create_alerts:
            return

        # We pre-fetch Journeys to optimize creating the alerts
        instances = Instance.select(Instance, Journey).join(Journey).where(Instance.id << [*create_alerts.keys()])

        for instance in instances:
            for alert_type in create_alerts[instance.id]:
                self.alerts.append(
                    create_instance_alert(
                        alert_type,
                        instance,
                        component=event.component,
                        alert_components=[cast(UUID, event.component_id)],
                    )
                )

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        run_id, task_id = None, None
        # 'component' and 'instance_set' have to be set in the context beforehand
        if not self.context.component:
            LOG.error("TestOutcomeHandler early exit due to required data missing from the context")
            return True
        if event.component_type == ComponentType.BATCH_PIPELINE:
            # If it is a batch-pipeline component, it must also tie to a run
            if (run := self.context.run) is None:
                LOG.error("TestOutcomeHandler early exit due 'run' missing from the context")
                return True
            run_id = run.id
            task_id = self.context.task.id if self.context.task is not None else None
        TestOutcomeService.insert_from_event(
            event=event,
            component_id=self.context.component.id,
            instance_set_id=self.context.instance_set.id if self.context.instance_set else None,
            run_id=run_id,
            task_id=task_id,
        )
        self.create_instance_alerts(event)
        return True
