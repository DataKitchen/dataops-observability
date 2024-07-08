__all__ = ("ProjectRule", "get_project_rules")

import logging
from typing import Callable, cast
from uuid import UUID

from peewee import DoesNotExist, fn

from common.entities import Project, Action, Company, Organization, Rule as RuleEntity
from rules_engine.actions import BaseAction, action_factory
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


def _get_actions_from_project(project: Project) -> list[BaseAction]:
    if not project.alert_actions:
        return []

    template_actions_query = (
        Action.select()
        .join(Company)
        .join(Organization)
        .join(Project)
        .where(Project.id == project.id, Action.action_impl.in_([pa["action_impl"] for pa in project.alert_actions]))
    )
    try:
        template_actions = {ta.action_impl.name: ta for ta in template_actions_query}
    except DoesNotExist:
        template_actions = {}

    actions = []
    for action in project.alert_actions:
        LOG.info(f"{template_actions}, {action} <- AQUI")

        actions.append(
            action_factory(
                action["action_impl"], action["action_args"], template_actions.get(action["action_impl"], None)
            )
        )
    return actions


def get_project_rules(project_id: UUID) -> list[ProjectRule]:
    rules: list[ProjectRule] = []
    try:
        project = (
            Project.select()
            .where(
                Project.id == project_id,
                Project.agent_status_check_interval > 0,
                fn.JSON_LENGTH(Project.alert_actions) > 0,
            )
            .get()
        )
    except Project.DoesNotExist:
        return rules

    def action_trigger(event: PROJECT_EVENT) -> None:
        actions = _get_actions_from_project(project)
        if actions:
            for action in actions:
                LOG.info("Executing action %s from project '%s'", action, project.id)
                action.execute(event, RuleEntity(), None)
        else:
            LOG.info("No actions found for project '%s', skipping", project.id)

    rules.append(ProjectRule(action_trigger))

    return rules
