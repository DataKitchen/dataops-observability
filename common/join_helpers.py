__all__ = ["join_until"]


from peewee import ModelSelect

from common import entities as e
from common.entities import BaseEntity

_JOIN_DICT: dict[type[BaseEntity], type[BaseEntity]] = {
    e.Rule: e.Journey,
    e.Component: e.Project,
    e.Dataset: e.Project,
    e.Journey: e.Project,
    e.Schedule: e.Component,
    e.Run: e.Pipeline,
    e.Pipeline: e.Project,
    e.Project: e.Organization,
    e.Organization: e.Company,
    e.Action: e.Company,
    e.ServiceAccountKey: e.Project,
    e.Instance: e.Journey,
    e.JourneyDagEdge: e.Journey,
    e.StreamingPipeline: e.Project,
    e.Server: e.Project,
    e.InstanceRule: e.Journey,
    e.TestOutcome: e.Component,
}


def join_until(query: ModelSelect, join_root: type[BaseEntity]) -> ModelSelect:
    """Returns a new query with chained joins added until the `join_root` entity is reached."""
    join_leaf = query.model
    while join_leaf != join_root:
        try:
            join_leaf = _JOIN_DICT[join_leaf]
        except KeyError as ke:
            raise ValueError(f"No known path to join '{join_leaf.__name__}' to '{join_root.__name__}'.") from ke
        query = query.join(join_leaf)
    return query
