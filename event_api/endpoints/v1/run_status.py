__all__ = ["RunStatus"]

from flask import Response

from common.events.v1 import RunStatusEvent

from .event_view import EventView


class RunStatus(EventView):
    event_type = RunStatusEvent

    def post(self) -> Response:
        """
        Run Status Event update CREATE
        ---
        tags: ["Events"]
        summary: RunStatus Event
        operationId: PostRunStatus
        description: Changes the status of a specified batch pipeline run or of a specified task in the run. Post a
                     RunStatus event to alert the system that a run has started and ended with a certain status or that
                     a task has started and ended with a certain status.
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
                        $ref: '#/components/schemas/RunStatusApiSchema'
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
