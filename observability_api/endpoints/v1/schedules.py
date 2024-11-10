__all__ = ["Schedules", "ScheduleById"]

import logging
from http import HTTPStatus
from uuid import UUID

from flask import Response, make_response
from werkzeug.exceptions import BadRequest, NotFound

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Component, ComponentType, Schedule, ScheduleExpectation
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import ScheduleSchema

LOG = logging.getLogger(__name__)

EXPECTATION_TO_COMPONENT = {
    ScheduleExpectation.BATCH_PIPELINE_START_TIME.value: ComponentType.BATCH_PIPELINE.value,
    ScheduleExpectation.BATCH_PIPELINE_END_TIME.value: ComponentType.BATCH_PIPELINE.value,
    ScheduleExpectation.DATASET_ARRIVAL.value: ComponentType.DATASET.value,
}
"""Maps the expectation type to the requried component type"""


class Schedules(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, component_id: UUID) -> Response:
        """
        Schedule LIST
        ---
        tags: ["Schedule"]
        description: "Lists all schedules for the given component. <br>
        The route observability/batch-pipelines/&lt;pipeline-id&gt;/schedules is deprecated and will be removed in a future release."
        operationId: ListSchedules
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: component_id
            description: the ID of the component being queried.
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - schedule list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/ScheduleSchema'
                    total:
                      type: integer
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Component not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        schedules = list(self.get_entity_or_fail(Component, Component.id == component_id).schedules)
        return make_response({"entities": ScheduleSchema().dump(schedules, many=True), "total": len(schedules)})

    def post(self, component_id: UUID) -> Response:
        """
        Schedule CREATE
        ---
        tags: ["Schedule"]
        operationId: PostSchedule
        description: "Creates a new schedule that sets the given component time-based expectations. <br>
        The route observability/batch-pipelines/&lt;pipeline-id&gt;/schedules is deprecated and will be removed in a future release."
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: component_id
            description: The ID of the component that the schedule will be created under.
            schema:
              type: string
            required: true
        requestBody:
          description: The data required for the new schedule.
          required: true
          content:
            application/json:
              schema: ScheduleSchema
        responses:
          201:
            description: Request successful - schedule created.
            content:
              application/json:
                schema: ScheduleSchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Component not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          409:
            description: Schedule with similar data already exists.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        schedule = self.parse_body(schema=ScheduleSchema())
        schedule.created_by = self.user
        schedule.component = self.get_entity_or_fail(Component, Component.id == component_id)
        if (component_type := EXPECTATION_TO_COMPONENT[schedule.expectation]) != schedule.component.type:
            raise BadRequest(f"Expectation {schedule.expectation} is only valid for component of type {component_type}")
        self.save_entity_or_fail(schedule, force_insert=True)
        return make_response(ScheduleSchema().dump(schedule), HTTPStatus.CREATED)


class ScheduleById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def delete(self, schedule_id: UUID) -> Response:
        """
        Delete a Schedule by ID
        ---
        tags: ["Schedule"]
        operationId: DeleteScheduleById
        description: Permanently deletes a single schedule by its ID.
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: schedule_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - schedule deleted.
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        try:
            self.get_entity_or_fail(Schedule, Schedule.id == schedule_id).delete_instance()
        except NotFound:
            # We don't care when the entity is not found since the outcome is the same
            pass
        return make_response("", HTTPStatus.NO_CONTENT)
