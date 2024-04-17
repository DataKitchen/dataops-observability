__all__ = ["Companies", "CompanyById"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import PERM_USER, PERM_USER_ADMIN, BaseView
from common.api.request_parsing import no_body_allowed
from common.entities import Company
from common.entity_services import CompanyService
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import CompanySchema

LOG = logging.getLogger(__name__)


class Companies(BaseView):
    PERMISSION_REQUIREMENTS = (PERM_USER_ADMIN,)

    @no_body_allowed
    def get(self) -> Response:
        """Company LIST
        ---
        tags: ["Company"]
        description: Lists all companies in the system.
        operationId: ListCompanies
        security:
        parameters:
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
            description: The sort order for the company list. The sort is applied to the list before pagination.
        responses:
          200:
            description: Request successful - company list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/CompanySchema'
                    total:
                      type: integer
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
        page: Page = CompanyService.list_with_rules(ListRules.from_params(request.args))
        companies = CompanySchema().dump(page.results, many=True)
        return make_response({"entities": companies, "total": page.total})


class CompanyById(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER_ADMIN("PATCH", "DELETE"), PERM_USER("GET"))

    @no_body_allowed
    def get(self, company_id: UUID) -> Response:
        """Get Company by ID
        ---
        tags: ["Company"]
        operationId: GetCompanyById
        description: Retrieves a single company by its ID.
        security:
        parameters:
          - in: path
            name: company_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - company returned.
            content:
              application/json:
                schema: CompanySchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
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
        company = self.get_entity_or_fail(Company, Company.id == company_id)
        return make_response(CompanySchema().dump(company))
