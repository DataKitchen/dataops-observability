__all__ = ("ProjectRule", "get_project_rules")

import logging
from typing import Callable, cast
from uuid import UUID

from peewee import fn

from common.entities import Project, Rule as RuleEntity
from common.entity_services import ProjectService
from rules_engine.typing import PROJECT_EVENT, EVENT_TYPE

LOG = logging.getLogger(__name__)


class ProjectRule:
    def __init__(self, callable: Callable[[PROJECT_EVENT], None]):
        self.callable = callable

    def evaluate(self, event: EVENT_TYPE) -> None:
        LOG.info("Result: TRUE")
        self.callable(cast(PROJECT_EVENT, event))

    def __str__(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}"


def get_project_rules(project_id: UUID) -> list[ProjectRule]:
    rules: list[ProjectRule] = []
    try:
        project = (
            Project.select()
            .where(
                Project.id == project_id,
                Project.agent_check_interval > 0,
                fn.JSON_LENGTH(Project.alert_actions) > 0,
            )
            .get()
        )
    except Project.DoesNotExist:
        return rules

    def action_trigger(event: PROJECT_EVENT) -> None:
        actions = ProjectService.get_alert_actions(project)
        if actions:
            for action in actions:
                LOG.info("Executing action %s from project '%s'", action, project.id)
                action.execute(event, RuleEntity(), None)
        else:
            LOG.info("No actions found for project '%s', skipping", project.id)

    rules.append(ProjectRule(action_trigger))

    return rules
