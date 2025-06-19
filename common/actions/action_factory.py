__all__ = ["ACTION_CLASS_MAP", "action_factory"]


from common.entities import Action

from common.actions.action import BaseAction, ImplementationNotFound, InvalidActionTemplate
from common.actions.send_email_action import SendEmailAction
from common.actions.webhook_action import WebhookAction

ACTION_CLASS_MAP: dict[str, type[BaseAction]] = {"CALL_WEBHOOK": WebhookAction, "SEND_EMAIL": SendEmailAction}


def action_factory(implementation: str, action_args: dict, template: Action | None) -> BaseAction:
    try:
        action_class = ACTION_CLASS_MAP[implementation]
    except KeyError as ke:
        raise ImplementationNotFound(f"Action implementation '{implementation}' is not recognized") from ke

    if template and template.action_impl.name != implementation:
        raise InvalidActionTemplate(
            f"Template '{template.id}' '{template.action_impl}' doesn't match Rule action '{implementation}'"
        )

    return action_class(template, action_args)
