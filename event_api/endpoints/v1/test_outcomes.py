__all__ = ["TestOutcomes"]

from flask import Response

from common.events.v1 import TestOutcomesEvent

from .event_view import EventView


class TestOutcomes(EventView):
    """Sends an event reporting the outcomes of a test."""

    event_type = TestOutcomesEvent

    def post(self) -> Response:
        """
        TestOutcomes Event CREATE
        ---
        summary: TestOutcomes Event
        operationId: PostTestOutcomes
        tags: ["Events"]
        description: Reports the outcomes of a test or a set of tests. Receives a list of test outcomes by test name and
                    status (PASSED, FAILED, or WARNING).

                    Post a TestOutcomesEvent event to send outcomes from an external tool to the Observe platform to
                    track and report on runs and outcomes.
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
                        $ref: '#/components/schemas/TestOutcomesApiSchema'
        responses:
            204:
                description: Event successfully created.
            400:
                description: There is invalid or missing data in the request body.
                content:
                    application/json:
                        schema: HTTPErrorSchema
            413:
                description: The event payload is too large and has to be split into smaller events.
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
