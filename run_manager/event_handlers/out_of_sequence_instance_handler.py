__all__ = ["OutOfSequenceInstanceHandler"]

import logging

from common.entities import ComponentType, Instance, InstanceAlert, InstanceAlertType, Journey
from common.entity_services import InstanceService, JourneyService
from common.events import EventHandlerBase
from common.events.internal import InstanceAlert as InstanceAlertEvent
from common.events.v1 import MessageLogEvent, MetricLogEvent, RunStatusEvent, TestOutcomesEvent
from run_manager.alerts import create_instance_alert, update_instances_alert_components
from run_manager.context import RunManagerContext

LOG = logging.getLogger(__name__)


class OutOfSequenceInstanceHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context
        self.alerts: list[InstanceAlertEvent] = []

    def handle_message_log(self, event: MessageLogEvent) -> bool:
        self.check_out_of_sequence()
        return True

    def handle_metric_log(self, event: MetricLogEvent) -> bool:
        self.check_out_of_sequence()
        return True

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        self.check_out_of_sequence()
        return True

    def handle_run_status(self, event: RunStatusEvent) -> bool:
        self.check_out_of_sequence()
        return True

    def check_out_of_sequence(self) -> None:
        if (
            self.context.component
            and self.context.component.component_type == ComponentType.BATCH_PIPELINE.name
            and self.context.started_run
            and self.context.run
        ):
            iq = (
                Instance.select(Instance, Journey)
                .join(Journey)
                .where(Instance.id.in_([i.instance for i in self.context.instances]))
            )
            instances = iq.prefetch(
                InstanceAlert.select().where(InstanceAlert.type == InstanceAlertType.OUT_OF_SEQUENCE)
            )
            update_alerts = []
            for instance in instances:
                if upstream_nodes := JourneyService.get_upstream_nodes(instance.journey, self.context.component.id):
                    finished_runs = InstanceService.get_instance_run_counts(
                        instance,
                        end_before=self.context.run.start_time,
                        pipelines=upstream_nodes,
                    )
                    unfinished_components = [comp for comp, run_ct in finished_runs.items() if run_ct == 0]
                    if unfinished_components:
                        if len(instance.instance_alerts) == 0:
                            self.alerts.append(
                                create_instance_alert(
                                    alert_type=InstanceAlertType.OUT_OF_SEQUENCE,
                                    instance=instance,
                                    alert_components=unfinished_components,
                                )
                            )
                        else:
                            update_alerts.extend(
                                [(instance.instance_alerts[0].id, comp_id) for comp_id in unfinished_components]
                            )
                            if len(instance.instance_alerts) > 1:
                                LOG.error(
                                    f"{len(instance.instance_alerts)} out-of-sequence alerts found in instance "
                                    f"{instance.id}. Expected at most 1 out-of-sequence instance alert per instance;"
                                )
            update_instances_alert_components(update_alerts)
