import logging
from http import HTTPStatus
from uuid import UUID

from flask import Response, make_response
from peewee import IntegrityError
from werkzeug.exceptions import Conflict, NotFound

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import InstanceRule, Journey
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import InstanceRulePostSchema, InstanceRuleSchema

LOG = logging.getLogger(__name__)


class InstanceRuleCreate(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    def post(self, journey_id: UUID) -> Response:
        """
        InstanceRule CREATE
        ---
        tags: ["InstanceRule"]
        operationId: PostInstanceRule
        description: Creates a new instance rule in a journey.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            description: The ID of the journey that the instance rule will be created under.
            schema:
              type: string
            required: true
        requestBody:
          description: The data required for the new instance rule.
          required: true
          content:
            application/json:
              schema: InstanceRulePostSchema
        responses:
          201:
            description: Request successful - instance rule created.
            content:
              application/json:
                schema: InstanceRuleSchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Journey not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          409:
            description: There is a data conflict with the information in the new instance rule.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        journey = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        instance_data = self.parse_body(schema=InstanceRulePostSchema())
        try:
            rule_data = {
                "journey": journey,
                "action": instance_data["action"],
                "batch_pipeline_id": instance_data.get("batch_pipeline"),
            }
            if schedule_data := instance_data.get("schedule"):
                rule_data["expression"] = schedule_data["expression"]
                rule_data["timezone"] = schedule_data["timezone"]
            instance_rule = InstanceRule.create(**rule_data)
        except IntegrityError as e:
            LOG.exception("Unable to create instance rule.")
            raise Conflict("Failed to create InstanceRule; database integrity error.") from e

        return make_response(InstanceRuleSchema().dump(instance_rule), HTTPStatus.CREATED)


class InstanceRuleById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def delete(self, *, instance_rule_id: UUID) -> Response:
        """
        Delete an InstanceRule by ID
        ---
        tags: ["InstanceRule"]
        operationId: DeleteInstanceRule
        description: Permanently deletes a single instance rule by its ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: instance_rule_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - instance rule deleted.
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
            rule = self.get_entity_or_fail(InstanceRule, InstanceRule.id == instance_rule_id)
        except NotFound:
            pass
        else:
            rule.delete_instance()
        return make_response("", HTTPStatus.NO_CONTENT)
