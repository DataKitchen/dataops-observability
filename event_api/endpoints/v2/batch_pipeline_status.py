__all__ = ["BatchPipelineStatusView"]

from flask import Response

from common.events.v2 import BatchPipelineStatusSchema, BatchPipelineStatusUserEvent

from .event_view import BaseEventView


class BatchPipelineStatusView(BaseEventView):
    payload_schema = BatchPipelineStatusSchema()
    event_type = BatchPipelineStatusUserEvent

    def post(self) -> Response:
        """
        Post a batch pipeline run status.
        ---
        tags: ["Events"]
        summary: Batch Pipeline Status Event
        operationId: PostBatchPipelineStatus
        description: Changes the status of a specified batch pipeline run or of a specified task in the run. Post a
                     BatchPipelineStatus event to alert the system that a run has started and ended with a certain status or that
                     a task has started and ended with a certain status.
        security:
            - SAKey: []
        requestBody:
            description: Data describing the event.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/BatchPipelineStatusSchema'
        responses:
            202:
                description: Event successfully created.
                content:
                  application/json:
                    schema:
                        $ref: '#/components/schemas/EventResponseSchema'
            400:
                description: There is invalid or missing data in the request body.
                content:
                    application/json:
                        schema: HTTPErrorSchema
            500:
                description: Unverified error. Consult the response body for more details.
                content:
                    application/json:
                        schema: HTTPErrorSchema
        """
        return super().post()
