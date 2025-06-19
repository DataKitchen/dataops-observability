from __future__ import annotations

__all__ = ["ListRules", "Page", "SortOrder", "DEFAULT_PAGE", "DEFAULT_COUNT", "ListSchema"]
from dataclasses import dataclass
from enum import Enum as std_Enum
from enum import auto
from typing import TypeVar
from collections.abc import Generator

from marshmallow import EXCLUDE, Schema
from marshmallow.fields import Enum, Int
from peewee import JOIN, Field, Ordering, Select
from werkzeug.datastructures import MultiDict

from common.entities import BaseEntity

DEFAULT_PAGE = 1
DEFAULT_COUNT = 10
T = TypeVar("T")


class SortOrder(std_Enum):
    ASC = auto()
    DESC = auto()


class ListSchema(Schema):
    page = Int(
        load_default=1, metadata={"description": "A page number to use for pagination. All pagination starts with 1."}
    )
    count = Int(load_default=10, metadata={"description": "The number of results to display per page."})
    sort = Enum(SortOrder, load_default=SortOrder.ASC, metadata={"description": "The sort order for the list."})

    class Meta:
        unknown = EXCLUDE


@dataclass
class Page[T]:
    """
    Useful for returning results from the service layer to get paginated results
    but also receive the total objects without pagination.
    """

    results: list[T]
    total: int

    def __iter__(self) -> Generator[T, None, None]:
        yield from self.results

    def __len__(self) -> int:
        return len(self.results)

    @classmethod
    def get_paginated_results(cls, query: Select, order_by: Field, list_rules: ListRules) -> Page[T]:
        model: BaseEntity = query.model
        ordering = list_rules.order_by_field(order_by)

        paginated_subquery: Select = (
            model.select(model.id)
            .where(query._where)
            .order_by(ordering)
            .paginate(list_rules.page, list_rules.count)
            .alias("results")
        )

        results_query = query.clone()
        results_query._where = None
        results_query = results_query.join(
            paginated_subquery, join_type=JOIN.INNER, on=(model.id == paginated_subquery.c.id)
        ).order_by(ordering)

        return cls(results=list(results_query), total=paginated_subquery.count(clear_limit=True))


@dataclass
class ListRules:
    """
    This is utilized for taking in the query parameters related to "listing" entities and parsing them into valid
    configurations that can be used by the Service layer to transform the results at the database query level.
    """

    page: int = DEFAULT_PAGE
    count: int = DEFAULT_COUNT
    sort: SortOrder = SortOrder.ASC
    search: str | None = None

    @classmethod
    def from_params_without_search(cls, params: MultiDict) -> ListRules:
        return cls(
            **ListSchema().load(params.to_dict()),
            search=None,
        )

    @classmethod
    def from_params(cls, params: MultiDict) -> ListRules:
        return cls(
            page=params.get("page", DEFAULT_PAGE, type=int),
            count=params.get("count", DEFAULT_COUNT, type=int),
            search=params.get("search", None, type=str),
            sort=(SortOrder.ASC if params.get("sort", "asc").lower() == "asc" else SortOrder.DESC),
        )

    def order_by_field(self, field: Field) -> Ordering:
        return field.asc() if self.sort == SortOrder.ASC else field.desc()
