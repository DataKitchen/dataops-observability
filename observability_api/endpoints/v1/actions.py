__all__ = ["Actions", "ActionById"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Action, Company
from common.entity_services import CompanyService
from common.entity_services.helpers import ActionFilters, ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import ActionSchema

LOG = logging.getLogger(__name__)


class Actions(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, company_id: UUID) -> Response:
        """Action LIST
        ---
        tags: ["Action"]
        description: List all actions configured for the company.
        operationId: ListActions
        security:
        parameters:
          - in: path
            name: company_id
            description: the ID of the company being queried.
            schema:
              type: string
            required: true
          - in: query
            name: action_impl
            schema:
              type: array
              items:
                type: string
            description: Optional. If specified, the results will be limited to actions with the listed types.
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
                          propertyName: action_impl
                          mapping:
                            SEND_EMAIL: '#/components/schemas/SendEmailActionSchema'
                            CALL_WEBHOOK: '#/components/schemas/CallWebhookActionSchema'
                        anyOf:
                          - $ref: '#/components/schemas/SendEmailActionSchema'
                          - $ref: '#/components/schemas/CallWebhookActionSchema'
                    total:
                      type: integer
          404:
            description: Company not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        _ = self.get_entity_or_fail(Company, Company.id == company_id)
        page: Page = CompanyService.get_actions_with_rules(
            company_id, ListRules.from_params(request.args), ActionFilters.from_params(request.args)
        )
        actions = ActionSchema().dump(page.results, many=True)
        LOG.debug("List Actions for company_id '%s'. Found %d entries.", company_id, page.total)
        return make_response({"entities": actions, "total": page.total})


class ActionById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    def patch(self, action_id: UUID) -> Response:
        """Update Action by ID
        ---
        tags: ["Action"]
        description: Updates attributes for a single action. Use this request to change configuration details for an action.
        operationId: PatchActionById
        security:
        parameters:
          - in: path
            name: action_id
            schema:
              type: string
            required: true
        requestBody:
          description: The update data for the action.
          required: true
          content:
            application/json:
              schema:
                discriminator:
                  propertyName: action_impl
                  mapping:
                    SEND_EMAIL: '#/components/schemas/SendEmailActionSchema'
                    CALL_WEBHOOK: '#/components/schemas/CallWebhookActionSchema'
                oneOf:
                  - $ref: '#/components/schemas/SendEmailActionSchema'
                  - $ref: '#/components/schemas/CallWebhookActionSchema'

        responses:
          200:
            description: Request successful - action updated.
            content:
              application/json:
                schema: ActionSchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Action not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        action = self.get_entity_or_fail(Action, Action.id == action_id)
        self.parse_body(schema=ActionSchema(action))
        self.save_entity_or_fail(action)
        return make_response(ActionSchema().dump(action))
