__all__ = ["SendEmailAction"]
import logging
from dataclasses import asdict
from typing import Optional
from uuid import UUID

from peewee import DoesNotExist

from common.email.email_service import EmailService
from common.entities import Journey, Rule
from common.events.internal import InstanceAlert, RunAlert, AgentStatusChangeEvent
from common.events.v1 import Event
from rules_engine.typing import EVENT_TYPE
from rules_engine.data_points import AlertDataPoints, DataPoints, AgentStatusChangeDataPoints

from .action import ActionResult, BaseAction

LOG = logging.getLogger(__name__)


class SendEmailAction(BaseAction):
    required_arguments = {"from_address", "recipients", "template"}
    requires_action_template = True

    def _run(self, event: EVENT_TYPE, rule: Rule, journey_id: Optional[UUID]) -> ActionResult:
        try:
            context = self._get_data_points(event, rule, journey_id)
        except Exception as e:
            return ActionResult(False, None, e)
        try:
            response = EmailService.send_email(
                self.arguments["smtp_config"],
                self.arguments["from_address"],
                self.arguments["recipients"],
                self.arguments["template"],
                context,
            )
        except Exception as e:
            return ActionResult(False, None, e)
        else:
            return ActionResult(True, response, None)

    def _get_data_points(
        self, event: EVENT_TYPE, rule: Rule, journey_id: Optional[UUID]
    ) -> dict | AgentStatusChangeDataPoints:
        """
        Get the data points to be used in the email template
        """

        context: dict | AgentStatusChangeDataPoints = dict()

        match event:
            case RunAlert() | InstanceAlert():
                try:
                    context["journey_name"] = Journey.get_by_id(journey_id).name
                except DoesNotExist:
                    context["journey_name"] = "N/A"

                context.update(asdict(event))
                data_points = AlertDataPoints(event, rule)
                context["alert_level"] = data_points.alert.level
                context["project_name"] = data_points.project.name
                context["alert_type"] = data_points.alert.type
                context["base_url"] = data_points.company.ui_url
                context["event_timestamp_formatted"] = data_points.event.event_timestamp_formatted
                context["run_expected_start_time"] = getattr(data_points.alert, "expected_start_time_formatted", None)
                context["run_expected_end_time"] = getattr(data_points.alert, "expected_end_time_formatted", None)
                try:
                    context["run_key"] = data_points.run.key
                except Exception:
                    LOG.exception("Error determining run_key")
                    context["run_key"] = "N/A"
                try:
                    context["run_name"] = data_points.run.name
                except Exception:
                    context["run_name"] = None
                if isinstance(event, RunAlert):
                    context["component_key"] = data_points.component.key
                    context["component_name"] = data_points.component.name
                context["rule_run_state_matches"] = data_points.rule.run_state_matches
                context["rule_consecutive_run_count"] = data_points.rule.run_state_count
                context["rule_group_by_run_name"] = data_points.rule.run_state_group_run_name
                context["rule_only_exact_count"] = data_points.rule.run_state_trigger_successive

            case Event():
                try:
                    context["journey_name"] = Journey.get_by_id(journey_id).name
                except DoesNotExist:
                    context["journey_name"] = "N/A"

                context.update(event.as_dict())
                e_data_points = DataPoints(event, rule)
                context["component_key"] = e_data_points.component.key
                context["component_name"] = e_data_points.component.name
                context["project_name"] = e_data_points.project.name
                context["run_expected_start_time"] = getattr(e_data_points.run, "expected_start_time_formatted", None)
                context["run_expected_end_time"] = getattr(e_data_points.run, "expected_end_time_formatted", None)
                context["event_timestamp_formatted"] = e_data_points.event.event_timestamp_formatted
                try:
                    context["task_name"] = e_data_points.task.name
                except Exception:
                    context["task_name"] = ""
                try:
                    context["run_task_start_time"] = e_data_points.run_task.start_time_formatted
                except AttributeError:
                    context["run_task_start_time"] = "N/A"
                except Exception:
                    LOG.exception("Error determining run_task_start_time")
                    context["run_task_start_time"] = "N/A"
                try:
                    context["base_url"] = e_data_points.company.ui_url
                except AttributeError:
                    context["base_url"] = ""
                try:
                    context["run_key"] = e_data_points.run.key
                except Exception:
                    LOG.exception("Error determining run_key")
                    context["run_key"] = "N/A"
                try:
                    context["run_name"] = e_data_points.run.name
                except Exception:
                    context["run_name"] = None
                context["rule_run_state_matches"] = e_data_points.rule.run_state_matches
                context["rule_consecutive_run_count"] = e_data_points.rule.run_state_count
                context["rule_group_by_run_name"] = e_data_points.rule.run_state_group_run_name
                context["rule_only_exact_count"] = e_data_points.rule.run_state_trigger_successive
            case AgentStatusChangeEvent():
                context = AgentStatusChangeDataPoints(event, rule)

        return context
