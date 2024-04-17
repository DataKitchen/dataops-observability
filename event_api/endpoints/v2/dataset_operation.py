_sdf_all__ = ["DatasetOperationView"]

from flask import Response

from common.events.v2 import DatasetOperationSchema, DatasetOperationUserEvent

from .event_view import BaseEventView


class DatasetOperationView(BaseEventView):
    payload_schema = DatasetOperationSchema()
    event_type = DatasetOperationUserEvent

    def post(self) -> Response:
        """
        Post dataset operation.
        ---
        summary: Dataset Operation Event
        operationId: PostDatasetOperation
        tags: ["Events"]
        description: Event reports that a read or write operation has occurred for the specified dataset.
        security:
            - SAKey: []
        requestBody:
            description: Data describing the event.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/DatasetOperationSchema'
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
