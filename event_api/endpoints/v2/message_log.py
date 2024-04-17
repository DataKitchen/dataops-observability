__all__ = ["MessageLogView"]

from flask import Response

from common.events.v2 import MessageLogSchema, MessageLogUserEvent

from .event_view import BaseEventView


class MessageLogView(BaseEventView):
    payload_schema = MessageLogSchema()
    event_type = MessageLogUserEvent

    def post(self) -> Response:
        """
        Post message log entries.
        ---
        tags: ["Events"]
        summary: Message Log Event
        operationId: PostMessageLog
        description: Logs string messages related to the given component.

                     Post a log event to capture error, warning, or debugging messages from external tools and scripts.
        security:
            - SAKey: []
        requestBody:
            description: Data describing the event.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/MessageLogSchema'
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
