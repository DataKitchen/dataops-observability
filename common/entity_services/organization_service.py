__all__ = ["OrganizationService"]

from common.entities import Project
from common.entity_services.helpers import ListRules
from common.entity_services.helpers.list_rules import Page


class OrganizationService:
    @staticmethod
    def get_projects_with_rules(org_id: str, rules: ListRules) -> Page[Project]:
        query = Project.organization == org_id

        if rules.search is not None:
            query &= Project.name ** f"%{rules.search}%"

        results = Project.select().where(query)
        return Page[Project].get_paginated_results(results, Project.name, rules)
