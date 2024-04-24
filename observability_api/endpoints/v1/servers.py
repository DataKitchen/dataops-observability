__all__ = ["ServerComponentById", "ServerComponents"]

from uuid import UUID

from flask import Response

from common.api.request_parsing import no_body_allowed
from common.entities import Server
from observability_api.endpoints.component_view import ComponentByIdAbstractView, ComponentListAbstractView
from observability_api.schemas import ComponentPatchSchema, ServerSchema


class ServerComponents(ComponentListAbstractView):
    route = "servers"
    entity = Server
    schema = ServerSchema

    def post(self, project_id: UUID) -> Response:
        """Create a new server component in the project"""
        return super().post(project_id)


class ServerComponentById(ComponentByIdAbstractView):
    route = "servers"
    entity = Server
    schema = ServerSchema
    patch_schema = ComponentPatchSchema

    @no_body_allowed
    def get(self, component_id: UUID) -> Response:
        """Get a server component by ID"""
        return super().get(component_id)

    def patch(self, component_id: UUID) -> Response:
        """Update a server component by ID"""
        return super().patch(component_id)
