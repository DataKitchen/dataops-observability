__all__ = ["BatchPipelineComponentById", "BatchPipelineComponents"]

from uuid import UUID

from flask import Response

from common.api.request_parsing import no_body_allowed
from common.entities import Pipeline
from observability_api.endpoints.component_view import ComponentByIdAbstractView, ComponentListAbstractView
from observability_api.schemas import ComponentPatchSchema, PipelineSchema


class BatchPipelineComponents(ComponentListAbstractView):
    route = "batch-pipelines"
    entity = Pipeline
    schema = PipelineSchema

    def post(self, project_id: UUID) -> Response:
        """Create a new batch-pipeline component in a project"""
        return super().post(project_id)


class BatchPipelineComponentById(ComponentByIdAbstractView):
    route = "batch-pipelines"
    entity = Pipeline
    schema = PipelineSchema
    patch_schema = ComponentPatchSchema

    @no_body_allowed
    def get(self, component_id: UUID) -> Response:
        """Get a batch-pipeline component by ID"""
        return super().get(component_id)

    def patch(self, component_id: UUID) -> Response:
        """Update a batch-pipeline component by ID"""
        return super().patch(component_id)
