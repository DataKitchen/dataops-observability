__all__ = ["TestOutcomesView"]

from flask import Response

from common.events.v2 import TestOutcomesSchema, TestOutcomesUserEvent

from .event_view import BaseEventView


class TestOutcomesView(BaseEventView):
    payload_schema = TestOutcomesSchema()
    event_type = TestOutcomesUserEvent

    def post(self) -> Response:
        """
        Post test outcomes.
        ---
        summary: Test Outcomes Event
        operationId: PostTestOutcomes
        tags: ["Events"]
        description: Reports the outcomes of a test or a set of tests. Receives a list of test outcomes by test name and
                    status (PASSED, FAILED, or WARNING).

                    Post a TestOutcomesEvent event to send test outcomes from an external tool to the Observability platform
                    to track and report on runs and outcomes.
        security:
            - SAKey: []
        requestBody:
            description: Data describing the event.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/TestOutcomesSchema'
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
