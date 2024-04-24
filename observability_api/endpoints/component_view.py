__all__ = ["ComponentByIdAbstractView", "ComponentListAbstractView"]

import logging
from http import HTTPStatus
from typing import Any, Optional, Type
from uuid import UUID

from flask import Blueprint, Response, make_response
from marshmallow_peewee import ModelSchema

from common.api.base_view import Permission
from common.entities import BaseEntity, Project
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas.component_schemas import ComponentPatchSchema

LOG = logging.getLogger(__name__)


class ComponentByIdAbstractView(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()
    route: str
    entity: Type[BaseEntity]
    schema: Type[ModelSchema]
    patch_schema: Optional[Type[ModelSchema]] = None

    def get(self, component_id: UUID) -> Response:
        component = self.get_entity_or_fail(self.entity, self.entity.id == component_id)
        return make_response(self.schema().dump(component), HTTPStatus.OK)

    def patch(self, component_id: UUID) -> Response:
        component = self.get_entity_or_fail(self.entity, self.entity.id == component_id)
        self.parse_body(schema=ComponentPatchSchema(component))
        self.save_entity_or_fail(component)
        return make_response(self.schema().dump(self.entity.get_by_id(component_id)))

    @classmethod
    def add_route(cls, bp: Blueprint, path: str) -> Any:
        view_func = cls.as_view(f"{cls.__name__}_components_by_id")
        bp.add_url_rule(
            path.format(cls.route),
            view_func=view_func,
            methods=["GET", "PATCH"],
        )
        return view_func


class ComponentListAbstractView(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()
    route: str
    entity: Type[BaseEntity]
    schema: Type[ModelSchema]

    def post(self, project_id: UUID) -> Response:
        component = self.parse_body(schema=self.schema())
        component.created_by = self.user
        component.project = self.get_entity_or_fail(Project, Project.id == project_id)
        self.save_entity_or_fail(component, force_insert=True)
        return make_response(self.schema().dump(component), HTTPStatus.CREATED)

    @classmethod
    def add_route(cls, bp: Blueprint, path: str) -> Any:
        view_func = cls.as_view(f"{cls.__name__}_components")
        bp.add_url_rule(
            path.format(cls.route),
            view_func=view_func,
            methods=["POST"],
        )
        return view_func
