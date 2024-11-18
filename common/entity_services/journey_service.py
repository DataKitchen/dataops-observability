__all__ = ["JourneyService"]

import logging
from typing import Optional
from uuid import UUID

from common.entities import Action, Company, Component, Journey, JourneyDagEdge, Organization, Project, Rule
from common.entity_services.helpers import ComponentFilters, ListRules, Page
from common.exceptions.service import MultipleActionsFound

LOG = logging.getLogger(__name__)


class JourneyService:
    @staticmethod
    def get_rules_with_rules(journey_id: UUID, list_rules: ListRules) -> Page[Rule]:
        query = Rule.select(Rule).where(Rule.journey == journey_id)
        LOG.debug("Retrieving rules for journey_id: %s. Found %d records.", journey_id, query.count())
        return Page[Rule].get_paginated_results(query, Rule.created_on, list_rules)

    @staticmethod
    def get_action_by_implementation(journey_id: UUID, action_impl: str) -> Optional[Action]:
        """
        Fetches an Action entity given a Journey ID and the action implementation.

        An Action is bound to a Rule by the entities hierarchy and the 'action_impl' argument. Given this, it's only
        possible to support one single Action entity of the same 'action_impl' within a Company, so this function
        raises MultipleActionsFound in case there's more than one match. Returns None if there's no match.

        :param journey_id: Journey ID
        :param action_impl: The action_impl to find within the company
        """
        actions: list[Action] = list(
            Action.select()
            .join(Company)
            .join(Organization)
            .join(Project)
            .join(Journey)
            .where(Journey.id == journey_id, Action.action_impl == action_impl)
        )

        if len(actions) > 1:
            raise MultipleActionsFound(
                f"Expected 1 {action_impl} Action but found {len(actions)} for journey {journey_id}."
            )

        try:
            return actions[0]
        except IndexError:
            return None

    @staticmethod
    def get_components_with_rules(journey_id: str, rules: ListRules, filters: ComponentFilters) -> Page[Component]:
        query = JourneyDagEdge.journey_id == journey_id
        if rules.search is not None:
            query &= Component.key ** f"%{rules.search}%"
        if filters.component_types:
            query &= Component.type.in_(filters.component_types)
        if filters.tools:
            query &= Component.tool.in_(filters.tools)
        join_on = (JourneyDagEdge.left == Component.id) | (JourneyDagEdge.right == Component.id)
        query = Component.select(Component).join(JourneyDagEdge, on=join_on).where(query).distinct()
        return Page[Component].get_paginated_results(query, Component.key, rules)

    @staticmethod
    def get_upstream_nodes(journey: Journey, component_id: UUID) -> set:
        journey_dag = journey.journey_dag
        upstream_nodes = set()
        queue = [next((node for node in journey_dag if node.id == component_id), None)]
        while queue:
            if cur := queue.pop(0):
                for edge in journey_dag[cur]:
                    if edge.left is not None:
                        upstream_nodes.add(edge.left_id)
                        queue.append(edge.left)
        return upstream_nodes
