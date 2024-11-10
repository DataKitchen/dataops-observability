__all__ = ["MetricLog"]

from flask import Response

from common.events.v1 import MetricLogEvent

from .event_view import EventView


class MetricLog(EventView):
    """Posts an event related to a piece of datum of interest to the user."""

    event_type = MetricLogEvent  # noqa: F811

    def post(self) -> Response:
        """
        Log Metric Event CREATE
        ---
        tags: ["Events"]
        summary: MetricLog Event
        operationId: PostMetricLog
        description: Logs the value of a user-defined datum of interest, such as a row count.

                     Post a MetricLog event to track the value of a metric through a run or for comparing the value of
                     the metric across multiple runs.
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
                        $ref: '#/components/schemas/MetricLogApiSchema'
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
