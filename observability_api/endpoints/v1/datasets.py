__all__ = ["DatasetComponentById", "DatasetComponents"]

from uuid import UUID

from flask import Response

from common.api.request_parsing import no_body_allowed
from common.entities import Dataset
from observability_api.endpoints.component_view import ComponentByIdAbstractView, ComponentListAbstractView
from observability_api.schemas import ComponentPatchSchema, DatasetSchema


class DatasetComponents(ComponentListAbstractView):
    route = "datasets"
    entity = Dataset
    schema = DatasetSchema

    def post(self, project_id: UUID) -> Response:
        """Create a new dataset component in the project"""
        return super().post(project_id)


class DatasetComponentById(ComponentByIdAbstractView):
    route = "datasets"
    entity = Dataset
    schema = DatasetSchema
    patch_schema = ComponentPatchSchema

    @no_body_allowed
    def get(self, component_id: UUID) -> Response:
        """Get a dataset component by ID"""
        return super().get(component_id)

    def patch(self, component_id: UUID) -> Response:
        """Update a dataset component by ID"""
        return super().patch(component_id)
