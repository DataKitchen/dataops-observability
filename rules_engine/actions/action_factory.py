__all__ = ["ACTION_CLASS_MAP", "action_factory"]

from typing import Optional, Type

from common.entities import Action, Rule

from .action import BaseAction, ImplementationNotFound, InvalidActionTemplate
from .send_email_action import SendEmailAction
from .webhook_action import WebhookAction

ACTION_CLASS_MAP: dict[str, Type[BaseAction]] = {"CALL_WEBHOOK": WebhookAction, "SEND_EMAIL": SendEmailAction}


def action_factory(rule: Rule, template: Optional[Action]) -> BaseAction:
    try:
        action_class = ACTION_CLASS_MAP[rule.action]
    except KeyError as e:
        raise ImplementationNotFound(f"Action '{e}' referenced by rule '{rule.id}' is not recognized")

    if template and template.action_impl.name != rule.action:
        raise InvalidActionTemplate(
            f"Template '{template.id}' '{template.action_impl}' doesn't match Rule action '{rule.action}'"
        )

    return action_class(template, rule.action_args)
