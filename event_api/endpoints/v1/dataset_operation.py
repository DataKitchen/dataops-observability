__all__ = ["DatasetOperation"]

from flask import Response

from common.events.v1 import DatasetOperationEvent

from .event_view import EventView


class DatasetOperation(EventView):
    event_type = DatasetOperationEvent

    def post(self) -> Response:
        """
        Dataset Operation Event CREATE
        ---
        tags: ["Events"]
        summary: DatasetOperation Event
        operationId: PostDatasetOperation
        description: Event reports that a read or write operation has occurred for the specified dataset.
        security:
            - SAKey: []
        parameters:
           - in: header
             name: EVENT-SOURCE
             description: Set the source of the event. If unset, the Event Ingestion API will assume the source of the
                          Event is API. Warning - This parameter is not intended for use by end users.
             schema:
                type: string
                default: API
                enum:
                    - USER
                    - SCHEDULER
                    - API
                    - RULES_ENGINE
             required: false
        requestBody:
            description: Data describing the event.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/DatasetOperationApiSchema'
        responses:
            204:
                description: Event successfully created.
            400:
                description: There is invalid or missing data in the request body.
                content:
                    application/json:
                        schema: HTTPErrorSchema
            413:
                description: The event payload is too large.
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
