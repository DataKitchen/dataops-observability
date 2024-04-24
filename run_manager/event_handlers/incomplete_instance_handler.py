import logging

from common.entities import FINISHED_RUN_STATUSES, Instance, InstanceAlertType, Journey, Project
from common.entity_services import InstanceService
from common.events.internal import InstanceAlert
from run_manager.alerts import create_instance_alert
from run_manager.context import RunManagerContext

LOG = logging.getLogger(__name__)


class IncompleteInstanceHandler:
    def __init__(self, context: RunManagerContext) -> None:
        self.context = context
        self.alerts: list[InstanceAlert] = []

    def check(self) -> None:
        for instance in self.context.ended_instances:
            completed_run_count = InstanceService.get_instance_run_counts(
                instance,
                include_run_statuses=FINISHED_RUN_STATUSES,
            )

            if not all(completed_run_count.values()):
                LOG.info("Instance '%s' ended with incomplete state", instance)
                self.alerts.append(
                    create_instance_alert(
                        InstanceAlertType.INCOMPLETE,
                        instance=Instance.select(Instance, Journey, Project)
                        .join(Journey)
                        .join(Project)
                        .where(Instance.id == instance)
                        .get(),
                    )
                )
