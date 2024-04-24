__all__ = ["StreamingPipelineComponentById", "StreamingPipelineComponents"]

from uuid import UUID

from flask import Response

from common.api.request_parsing import no_body_allowed
from common.entities import StreamingPipeline
from observability_api.endpoints.component_view import ComponentByIdAbstractView, ComponentListAbstractView
from observability_api.schemas import ComponentPatchSchema, StreamingPipelineSchema


class StreamingPipelineComponents(ComponentListAbstractView):
    route = "streaming-pipelines"
    entity = StreamingPipeline
    schema = StreamingPipelineSchema

    def post(self, project_id: UUID) -> Response:
        """Create a new streaming-pipeline component in the project"""
        return super().post(project_id)


class StreamingPipelineComponentById(ComponentByIdAbstractView):
    route = "streaming-pipelines"
    entity = StreamingPipeline
    schema = StreamingPipelineSchema
    patch_schema = ComponentPatchSchema

    @no_body_allowed
    def get(self, component_id: UUID) -> Response:
        """Get a streaming-pipeline component by ID"""
        return super().get(component_id)

    def patch(self, component_id: UUID) -> Response:
        """Update a streaming-pipeline component by ID"""
        return super().patch(component_id)
