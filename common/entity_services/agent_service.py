__all__ = ["get_agents_with_rules"]

from common.entities import Agent
from common.entity_services.helpers import ListRules
from common.entity_services.helpers.list_rules import Page


def get_agents_with_rules(project_id: str, rules: ListRules) -> Page[Agent]:
    base_query = Agent.project == project_id
    if rules.search is not None:
        search_query = (Agent.key ** f"%{rules.search}%") | (Agent.tool ** f"%{rules.search}%")
        base_query &= search_query
    query = Agent.select().where(base_query)
    results = query.order_by(rules.order_by_field(Agent.key)).paginate(rules.page, rules.count)
    return Page[Agent](results=results, total=query.count())
