from functools import partial
from collections.abc import Iterable
from collections.abc import Callable

from peewee import PREFETCH_TYPE, Model, SelectQuery


def limit_query(limit: int) -> Callable[..., Iterable]:
    def _limit_query(query: SelectQuery, *, _limit: int) -> SelectQuery:
        return query.limit(_limit)

    return partial(_limit_query, _limit=limit)


def prefetch_query(*args: SelectQuery | type[Model]) -> Callable[..., Iterable]:
    def _prefetch_query(query: SelectQuery, *, _queries: list) -> list[Model]:
        result: list[Model] = query.prefetch(*_queries, prefetch_type=PREFETCH_TYPE.JOIN)
        return result

    return partial(_prefetch_query, _queries=list(args))
