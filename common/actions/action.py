__all__ = [
    "ActionException",
    "ImplementationNotFound",
    "InvalidActionTemplate",
    "ActionResult",
    "BaseAction",
    "ActionTemplateRequired",
]

import logging
from typing import Any, NamedTuple, Optional
from uuid import UUID

from common.entities import Action, Rule
from rules_engine.typing import EVENT_TYPE

LOG = logging.getLogger(__name__)


class ActionException(Exception):
    pass


class ImplementationNotFound(ActionException):
    pass


class ActionTemplateRequired(ActionException):
    pass


class InvalidActionTemplate(ActionException):
    pass


class ActionResult(NamedTuple):
    result: bool
    response: Optional[dict]
    exception: Optional[Exception]


class BaseAction:
    required_arguments: set = set()
    requires_action_template: bool = False

    def __init__(self, action_template: Optional[Action], override_arguments: dict) -> None:
        if self.requires_action_template and not action_template:
            raise ActionTemplateRequired(f"'{self.__class__.__name__}' requires an action template to be set")

        self.action_template = action_template
        self.override_arguments = override_arguments
        self.arguments = self._build_arguments()
        self._validate_args()

    def _build_arguments(self) -> dict[str, Any]:
        arguments: dict[str, Any] = {}
        if self.action_template:
            arguments.update(self.action_template.action_args)
        arguments.update(self.override_arguments)
        LOG.info(
            "Built %s's argument list using action template '%s': %r",
            self.__class__.__name__,
            self.action_template,
            arguments,
        )
        return arguments

    def _validate_args(self) -> None:
        missing_args = self.__class__.required_arguments - self.arguments.keys()
        if missing_args:
            raise ValueError(f"Required arguments {missing_args} missing for {self.__class__.__name__}")

    def _run(self, event: EVENT_TYPE, rule: Rule, journey_id: Optional[UUID]) -> ActionResult:
        raise NotImplementedError("Base Action cannot be executed")

    def _store_action_result(self, action_result: ActionResult) -> None:
        if action_result.result:
            LOG.info(
                "Action %s execution completed",
                self.__class__.__name__,
                extra={"response": action_result.response},
            )
        else:
            LOG.error(
                "Action %s execution failed",
                self.__class__.__name__,
                extra={"response": action_result.response},
                exc_info=action_result.exception,
            )

    def execute(self, event: EVENT_TYPE, rule: Rule, journey_id: Optional[UUID]) -> bool:
        action_result = self._run(event, rule, journey_id)
        self._store_action_result(action_result)
        return action_result.result
