from common.entities import Project, ServiceAccountKey
from common.entity_services.helpers import ListRules, Page


class ServiceAccountKeyService:
    @staticmethod
    def list_with_rules(*, project: Project, rules: ListRules) -> Page[ServiceAccountKey]:
        query = ServiceAccountKey.project == project
        if rules.search is not None:
            query &= (ServiceAccountKey.name ** f"%{rules.search}%") | (
                ServiceAccountKey.description ** f"%{rules.search}%"
            )
        results = ServiceAccountKey.select().where(query)
        return Page[ServiceAccountKey].get_paginated_results(results, ServiceAccountKey.name, rules)
