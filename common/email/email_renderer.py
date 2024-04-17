from typing import Callable

from pybars import Compiler

from common.constants.email_templates import *
from common.email.templates import *

TEMPLATES: dict[str, type[BaseTemplate]] = {
    INSTANCE_ALERT_TEMPLATE_NAME: InstanceAlertTemplate,
    MESSAGE_LOG_TEMPLATE_NAME: MessageLogTemplate,
    METRIC_LOG_TEMPLATE_NAME: MetricLogTemplate,
    RUN_STATE_TEMPLATE_NAME: RunStateTemplate,
    TASK_STATUS_COMPLETED_TEMPLATE_NAME: TaskStatusCompletedTemplate,
    TASK_STATUS_ERROR_TEMPLATE_NAME: TaskStatusErrorTemplate,
    TASK_STATUS_MISSING_TEMPLATE_NAME: TaskStatusMissingTemplate,
    TASK_STATUS_PENDING_TEMPLATE_NAME: TaskStatusPendingTemplate,
    TASK_STATUS_STARTED_TEMPLATE_NAME: TaskStatusStartedTemplate,
    TASK_STATUS_WARNING_TEMPLATE_NAME: TaskStatusWarningTemplate,
    TEST_STATUS_TEMPLATE_NAME: TestStatusTemplate,
}


class HandlebarsEmailRenderer:

    @staticmethod
    def render(template_name: str, context_vars: dict) -> tuple[str, str]:
        if template_name not in TEMPLATES:
            raise ValueError(f"Template name {template_name} is not a valid selection for email action")
        template = TEMPLATES[template_name]
        template(**context_vars)
        compiled_template: Callable[..., str] = Compiler().compile(template.content)
        rendered_template = compiled_template(context_vars)
        return rendered_template, template.subject
