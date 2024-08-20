__all__ = ["CompanyService"]

from uuid import UUID

from common.entities import Action, Company, Organization, User
from common.entity_services.helpers import ActionFilters, ListRules
from common.entity_services.helpers.list_rules import Page


class CompanyService:
    """
    NOTE: Unless something drastically changes, all methods in here should be @staticmethod.
    Currently, there is nothing that needs to be instantiated for the class, so we can get away with
    not having to instantiate it on usage.
    """

    @staticmethod
    def list_with_rules(rules: ListRules) -> Page[Company]:
        query = Company.select()
        return Page[Company].get_paginated_results(query, Company.name, rules)

    @staticmethod
    def get_organizations_with_rules(company_id: str, rules: ListRules) -> Page[Organization]:
        query = Organization.select().where(Organization.company == company_id)
        return Page[Organization].get_paginated_results(query, Organization.name, rules)

    @staticmethod
    def get_users_with_rules(company_id: str, rules: ListRules) -> Page[User]:
        query = User.select().join(Company).where(User.primary_company == company_id)
        return Page[User].get_paginated_results(query, User.name, rules)

    @staticmethod
    def get_actions_with_rules(company_id: UUID, rules: ListRules, filters: ActionFilters) -> Page[Action]:
        query = Action.company == company_id
        if filters.action_impls:
            query &= Action.action_impl.in_(filters.action_impls)
        results = Action.select().where(query)
        return Page[Action].get_paginated_results(results, Action.name, rules)
