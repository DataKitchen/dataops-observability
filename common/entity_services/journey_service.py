__all__ = ["JourneyService"]

import logging
from fnmatch import fnmatch
from typing import Optional
from uuid import UUID

from common.entities import DB, Action, Company, Component, Journey, JourneyDagEdge, Organization, Project, Rule
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
        join_on = (JourneyDagEdge.journey_id == journey_id) & (
            (JourneyDagEdge.left == Component.id) | (JourneyDagEdge.right == Component.id)
        )
        query = Component.select(Component).join(JourneyDagEdge, on=join_on)
        if rules.search is not None:
            query = query.where(Component.key ** f"%{rules.search}%")
        if filters.component_types:
            query = query.where(Component.type.in_(filters.component_types))
        if filters.tools:
            query = query.where(Component.tool.in_(filters.tools))

        return Page[Component].get_paginated_results(query.distinct(), Component.key, rules)

    @staticmethod
    def parse_patterns(patterns_str: str | None) -> list[str]:
        if not patterns_str:
            return []
        return [p.strip() for p in patterns_str.replace("\n", ",").split(",") if p.strip()]

    @staticmethod
    def get_components_matching_patterns(
        project_id: str, include_patterns: list[str], exclude_patterns: list[str]
    ) -> list[Component]:
        if not include_patterns:
            return []
        components: list[Component] = list(Component.select().where(Component.project == project_id))
        return [
            c
            for c in components
            if any(fnmatch(c.key, p) for p in include_patterns) and not any(fnmatch(c.key, p) for p in exclude_patterns)
        ]

    @staticmethod
    def apply_component_patterns(journey: Journey) -> None:
        include_patterns = JourneyService.parse_patterns(journey.component_include_patterns)
        exclude_patterns = JourneyService.parse_patterns(journey.component_exclude_patterns)

        with DB.atomic():
            existing_edges = list(
                JourneyDagEdge.select().where(JourneyDagEdge.journey == journey, JourneyDagEdge.left.is_null(False))
            )
            JourneyDagEdge.delete().where(JourneyDagEdge.journey == journey).execute()

            if not include_patterns:
                return

            matching = JourneyService.get_components_matching_patterns(
                journey.project_id, include_patterns, exclude_patterns
            )
            matching_ids = {c.id for c in matching}

            restored_edges = [e for e in existing_edges if e.left_id in matching_ids and e.right_id in matching_ids]
            has_predecessor = {e.right_id for e in restored_edges}

            for component in matching:
                if component.id not in has_predecessor:
                    JourneyDagEdge(journey=journey, left=None, right=component).save(force_insert=True)

            for edge in restored_edges:
                JourneyDagEdge(journey=journey, left=edge.left, right=edge.right).save(force_insert=True)

    @staticmethod
    def add_component_to_matching_journeys(component: Component) -> None:
        journeys = list(
            Journey.select().where(
                Journey.project == component.project_id,
                Journey.component_include_patterns.is_null(False),
            )
        )
        for journey in journeys:
            include_patterns = JourneyService.parse_patterns(journey.component_include_patterns)
            exclude_patterns = JourneyService.parse_patterns(journey.component_exclude_patterns)
            if not include_patterns:
                continue
            if any(fnmatch(component.key, p) for p in include_patterns) and not any(
                fnmatch(component.key, p) for p in exclude_patterns
            ):
                JourneyDagEdge(journey=journey, left=None, right=component).save(force_insert=True)

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
