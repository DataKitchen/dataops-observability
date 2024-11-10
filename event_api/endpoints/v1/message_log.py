__all__ = ["MessageLog"]

from flask import Response

from common.events.v1 import MessageLogEvent

from .event_view import EventView


class MessageLog(EventView):
    """Post a message log to the system."""

    event_type = MessageLogEvent

    def post(self) -> Response:
        """
        Log Message Event CREATE
        ---
        tags: ["Events"]
        summary: MessageLog Event
        operationId: PostMessageLog
        description: Logs a string message related to the pipeline run, and optionally related to a specific task.
                     Post a MessageLog event to capture error, warning, or debugging messages from external tools and
                     scripts.
        security:
            - SAKey: []

        Parameters
        ----------
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
                        $ref: '#/components/schemas/MessageLogEventApiSchema'
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
