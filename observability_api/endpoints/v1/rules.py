__all__ = ["Rules", "RuleById"]

import logging
from http import HTTPStatus
from pprint import pformat
from uuid import UUID

from flask import Response, make_response, request
from peewee import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound

from common.actions.action import ActionTemplateRequired, ActionException
from common.actions.action_factory import action_factory
from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import DB, Component, Journey, Rule
from common.entity_services import JourneyService
from common.entity_services.helpers import ListRules, Page
from common.exceptions.service import MultipleActionsFound
from common.predicate_engine.compilers import compile_schema
from common.predicate_engine.exceptions import InvalidRuleData
from common.predicate_engine.schemas.simple_v1 import RuleDataSchema
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import RulePatchSchema, RuleSchema

LOG = logging.getLogger(__name__)


def _validate_rule_action(rule: Rule) -> None:
    """Validate that the current rule data is able to correctly generate an executable Action."""
    try:
        action = JourneyService.get_action_by_implementation(rule.journey, rule.action)
        action_factory(rule.action, rule.action_args, action)
    except ActionTemplateRequired as atr:
        LOG.exception("Action '%s' not configured.", rule.action)
        raise InternalServerError(f"Action '{rule.action}' not configured, contact system administrator.") from atr
    except (MultipleActionsFound, ActionException) as ae:
        LOG.exception("Action '%s' misconfigured.", rule.action)
        raise InternalServerError(f"Action '{rule.action}' misconfigured, contact system administrator.") from ae


def _validate_rule_predicate(rule: Rule) -> None:
    """Validate that the rule data compiles."""
    try:
        parsed_rule_data = RuleDataSchema().load(rule.rule_data)
        compile_schema(rule.rule_schema, parsed_rule_data)
    except InvalidRuleData as ird:
        LOG.exception("Invalid rule pattern.\nRule data: %s", pformat(rule.rule_data))
        raise BadRequest("Invalid rule pattern.") from ird


class Rules(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, journey_id: UUID) -> Response:
        """
        Rule LIST
        ---
        tags: ["Rule"]
        description: List all rules that attached to a journey.
        operationId: ListRules
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: journey_id
            description: the ID of the journey being queried.
            schema:
              type: string
            required: true
          - in: query
            name: page
            schema:
              type: integer
              default: 1
            description: A page number to use for pagination. All pagination starts with 1.
          - in: query
            name: count
            schema:
              type: integer
              default: 10
            description: The number of results to display per page.
          - in: query
            name: sort
            schema:
              type: string
              default: ASC
              enum:
                - ASC
                - DESC
            description: The sort order for the rules list. The sort is applied to the list before pagination.
        responses:
          200:
            description: Request successful - Rules list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        discriminator:
                          propertyName: action
                          mapping:
                            SEND_EMAIL: '#/components/schemas/SendEmailRuleSchema'
                            CALL_WEBHOOK: '#/components/schemas/CallWebhookRuleSchema'
                        anyOf:
                          - $ref: '#/components/schemas/SendEmailRuleSchema'
                          - $ref: '#/components/schemas/CallWebhookRuleSchema'
                    total:
                      type: integer
          404:
            description: Journey not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        _ = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        page: Page = JourneyService.get_rules_with_rules(journey_id, ListRules.from_params(request.args))
        rules = RuleSchema().dump(page.results, many=True)
        LOG.debug("List Rules for journey_id '%s'. Found %d entries.", journey_id, page.total)
        return make_response({"entities": rules, "total": page.total})

    def post(self, journey_id: UUID) -> Response:
        """
        Rule CREATE
        ---
        tags: ["Rule"]
        operationId: PostRule
        description: Creates a new rule associated with a Journey.
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: journey_id
            description: The ID of journey that the rule will be created under.
            schema:
              type: string
            required: true
        requestBody:
          description: The data required for the new rule.
          required: true
          content:
            application/json:
              schema:
                discriminator:
                  propertyName: action
                  mapping:
                    SEND_EMAIL: '#/components/schemas/SendEmailRuleSchema'
                    CALL_WEBHOOK: '#/components/schemas/CallWebhookRuleSchema'
                oneOf:
                  - $ref: '#/components/schemas/SendEmailRuleSchema'
                  - $ref: '#/components/schemas/CallWebhookRuleSchema'
        responses:
          201:
            description: Request successful - rule created.
            content:
              application/json:
                schema: RuleSchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Journey or Component not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          409:
            description: There is a data conflict with the information in the new rule.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        _ = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        rule = self.parse_body(schema=RuleSchema())
        rule.journey = journey_id

        if rule.component_id is not None:
            if not Component.select().where(Component.id == rule.component_id).exists():
                LOG.warning("Component '%s' not found under Journey '%s'.", rule.component_id, journey_id)
                raise NotFound(f"Component '{rule.component_id}' not found under journey '{journey_id}'.")

        _validate_rule_action(rule)
        _validate_rule_predicate(rule)

        with DB.atomic():
            try:
                rule.save(force_insert=True)
            except IntegrityError as ie:
                LOG.exception("Rule CREATE failed.")
                raise Conflict("Failed to create Rule; one already exists with that information.") from ie
        return make_response(RuleSchema().dump(rule), HTTPStatus.CREATED)


class RuleById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, rule_id: UUID) -> Response:
        """
        Get Rule by ID
        ---
        tags: ["Rule"]
        description: Retrieves the details of a single rule by its ID.
        security:
          - SAKey: []
        operationId: GetRuleById
        parameters:
          - in: path
            name: rule_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - rule details returned.
            content:
              application/json:
                schema:
                  discriminator:
                    propertyName: action
                    mapping:
                      SEND_EMAIL: '#/components/schemas/SendEmailRuleSchema'
                      CALL_WEBHOOK: '#/components/schemas/CallWebhookRuleSchema'
                  oneOf:
                    - $ref: '#/components/schemas/SendEmailRuleSchema'
                    - $ref: '#/components/schemas/CallWebhookRuleSchema'
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Rule not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        rule = self.get_entity_or_fail(Rule, Rule.id == rule_id)
        return make_response(RuleSchema().dump(rule))

    def patch(self, rule_id: UUID) -> Response:
        """
        Update Rule by ID
        ---
        tags: ["Rule"]
        description: Updates attributes for a single rule. Use this request to change a rule name and description
                     or set its status to active or inactive.
        operationId: PatchRuleById
        security:
        parameters:
          - in: path
            name: rule_id
            schema:
              type: string
            required: true
        requestBody:
          description: The update data for the rule.
          required: true
          content:
            application/json:
              schema:
                discriminator:
                  propertyName: action
                  mapping:
                    SEND_EMAIL: '#/components/schemas/RulePatchSendEmailSchema'
                    CALL_WEBHOOK: '#/components/schemas/CallWebhookRuleSchema'
                oneOf:
                  - $ref: '#/components/schemas/RulePatchSendEmailSchema'
                  - $ref: '#/components/schemas/CallWebhookRuleSchema'

        responses:
          200:
            description: Request successful - rule updated.
            content:
              application/json:
                schema: RuleSchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Rule not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        rule = self.get_entity_or_fail(Rule, Rule.id == rule_id)

        self.parse_body(schema=RulePatchSchema(rule))
        _validate_rule_action(rule)
        _validate_rule_predicate(rule)

        if (
            any("component" == f.name for f in rule.dirty_fields)
            and rule.component_id
            and not Component.select().where(Component.id == rule.component_id).exists()
        ):
            LOG.warning("Component '%s' not found under Journey '%s'.", rule.component_id, rule.journey_id)
            raise NotFound(f"Component '{rule.component_id}' not found under journey '{rule.journey_id}'.")

        try:
            rule.save()
        except IntegrityError as e:
            LOG.exception("Rule PATCH failed.")
            raise Conflict("Failed to patch Rule.") from e

        return make_response(RuleSchema().dump(rule))

    @no_body_allowed
    def delete(self, rule_id: UUID) -> Response:
        """
        Delete a Rule by ID
        ---
        tags: ["Rule"]
        operationId: DeleteRuleById
        description: Permanently deletes a single rule by its ID.
        security:
        parameters:
          - in: path
            name: rule_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - rule deleted.
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
            self.get_entity_or_fail(Rule, Rule.id == rule_id).delete_instance()
        except NotFound:
            pass
        return make_response("", HTTPStatus.NO_CONTENT)
