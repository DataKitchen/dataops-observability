from typing import Any, Optional, Type

from flask import Blueprint, Response, request
from flask.typing import RouteCallable
from marshmallow import Schema
from marshmallow.fields import Nested
from werkzeug.datastructures import MultiDict

from common.api.base_view import BaseView, SearchableView

SEARCH_ENDPOINT: str = "search"


class SearchView(BaseView):
    args_from_post: Optional[MultiDict] = None
    request_body_schema: Type[Schema]

    def post(self, *args: Any, **kwargs: Any) -> Response:
        self.parse_body(schema=self.request_body_schema())
        self.args_from_post = MultiDict(self.request_body.get("params", {}))
        return self.get(*args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> Response:
        raise NotImplementedError

    @property
    def args(self) -> MultiDict:
        return self.args_from_post or request.args


def add_route_with_search(bp: Blueprint, rule: str, view_func: RouteCallable, **options: Any) -> RouteCallable:
    bp.add_url_rule(rule, view_func=view_func, **options)

    view_class: Type[SearchableView] = view_func.view_class  # type: ignore [union-attr]
    view_name = f"{view_class.__name__}Search"
    search_schema = type(f"{view_name}FilterSchema", (Schema,), {"params": Nested(view_class.FILTERS_SCHEMA)})

    search_view_class: Type[BaseView] = type(
        view_name,
        (view_class, SearchView),
        {"request_body_schema": search_schema},
    )
    search_view_func: RouteCallable = search_view_class.as_view(f"{view_class.__name__.lower()}_search")

    search_rule = "/".join((rule.rstrip("/"), SEARCH_ENDPOINT))
    bp.add_url_rule(search_rule, view_func=search_view_func, methods=["POST"])
    return search_view_func
