from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional, Type

from flask import g, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from marshmallow import Schema, ValidationError
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest, Forbidden

from common.constants import ADMIN_ROLE
from common.entities import Project, User

LOG = logging.getLogger(__name__)


@dataclass
class Permission:
    entity_attribute: str
    role: Optional[str] = None
    methods: tuple[str, ...] = ("GET", "PUT", "POST", "PATCH", "DELETE")

    def __call__(self, *methods: str) -> Permission:
        return Permission(self.entity_attribute, self.role, methods)


PERM_USER = Permission("user")
PERM_USER_ADMIN = Permission("user", ADMIN_ROLE)
PERM_PROJECT = Permission("project")


class SearchableView(MethodView):
    FILTERS_SCHEMA: Type[Schema]


class BaseView(MethodView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...]
    """
    A tuple of permissions required to access the view.

    For authentication exempted route, such as sso_login, use an empty tuple. Otherwise, at least one permission must be
    defined. The request is dispatched when the first valid permission met, i.e. the elements of this tuple are "OR'ed"
    """

    @property
    def user(self) -> Optional[User]:
        """Return the currently authenticated user."""
        return getattr(g, "user", None)

    @property
    def user_roles(self) -> list[str]:
        """Return a list of the roles of which the current user is a member."""
        if user := self.user:
            return user.user_roles
        else:
            return []

    @property
    def claims(self) -> Optional[User]:
        """Return the currently authenticated token."""
        return getattr(g, "claims", None)

    @property
    def project(self) -> Optional[Project]:
        return getattr(g, "project", None)

    @property
    def is_admin(self) -> bool:
        """Determine if the current user is a member of the admin group."""
        return ADMIN_ROLE in self.user_roles

    @cached_property
    def request_body(self) -> dict[str, Any]:
        """Parse and return the JSON body from the flask request."""
        if not request.is_json:
            raise BadRequest("Invalid content-type. Expected `application/json`")

        request_body = request.form or request.json
        if request_body is None and request.data is not None:
            try:
                request_body = json.loads(request.data)
            except json.JSONDecodeError:
                raise BadRequest("The request does not contain a valid JSON body")
        return request_body

    def parse_body(self, *, schema: Schema) -> Any:
        """Parse the response body using the given schema."""
        data = self.request_body
        try:
            return schema.load(data)
        except ValidationError as e:
            raise BadRequest(str(e)) from e

    def parse_args(self, *, schema: Schema) -> Any:
        """Parse the request arguments using the given schema."""
        try:
            return schema.load(request.args)
        except ValidationError as e:
            raise BadRequest(str(e)) from e

    @property
    def args(self) -> MultiDict:
        """
        Returns the request.args MultiDict.

        The main utility of this property is to allow subclasses to override it.
        """
        return request.args

    def validate_permissions(self) -> None:
        """Raise 403 error when access requirements are not met."""
        if request.method not in ("GET", "PUT", "POST", "PATCH", "DELETE"):
            return

        if not self.PERMISSION_REQUIREMENTS:
            return

        for perm in self.PERMISSION_REQUIREMENTS:
            access_allowed = all(
                (
                    getattr(g, perm.entity_attribute, None) is not None,
                    perm.role is None or perm.role in self.user_roles,
                    request.method in perm.methods,
                )
            )

            if access_allowed:
                return

        raise Forbidden()

    def dispatch_request(self, *args: Any, **kwargs: Any) -> ResponseReturnValue:
        # Role requests are only required for a subset of verbs.
        self.validate_permissions()

        return super().dispatch_request(*args, **kwargs)
