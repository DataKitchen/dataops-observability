__all__ = ["MetricLogView"]

from flask import Response

from common.events.v2 import MetricLogSchema, MetricLogUserEvent

from .event_view import BaseEventView


class MetricLogView(BaseEventView):
    payload_schema = MetricLogSchema()
    event_type = MetricLogUserEvent

    def post(self) -> Response:
        """
        Post metric log entries.
        ---
        tags: ["Events"]
        summary: Metric Log Event
        operationId: PostMetricLog
        description: Values of a user-defined datum of interest, such as a row count.

                     It can be used to track metric values through a run or compare metric values across
                     multiple runs.
        security:
            - SAKey: []
        requestBody:
            description: Data describing the event.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/MetricLogSchema'
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
