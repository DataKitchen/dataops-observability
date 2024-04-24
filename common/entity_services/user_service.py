from typing import Optional

from common.entities import User
from common.entity_services.helpers import ListRules, Page


class UserService:
    @staticmethod
    def list_with_rules(
        rules: ListRules, company_id: Optional[str] = None, name_filter: Optional[str] = None
    ) -> Page[User]:
        query = User.select()
        if company_id:
            query = query.where(User.primary_company_id == company_id)
        if name_filter:
            query = query.where(User.name.contains(name_filter))
        return Page[User].get_paginated_results(query, User.name, rules)
