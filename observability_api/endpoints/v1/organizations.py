__all__ = ["Organizations", "OrganizationById"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import PERM_USER, Permission
from common.api.request_parsing import no_body_allowed
from common.entities import DB, Company, Organization  # noqa: F401
from common.entity_services import CompanyService
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas.organization_schemas import OrganizationSchema

LOG = logging.getLogger(__name__)


class Organizations(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER,)

    @no_body_allowed
    def get(self, company_id: UUID) -> Response:
        """Organization LIST
        ---
        tags: ["Organization"]
        description: Lists all organizations in a company using the specified company ID.
        operationId: ListOrganizations
        security:
        parameters:
          - in: path
            name: company_id
            description: the ID of the requested company.
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
            description: The sort order for the organization list. The sort is applied to the list before pagination.
        responses:
          200:
            description: Request successful - organization list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/OrganizationSchema'
                    total:
                      type: integer
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
        _ = self.get_entity_or_fail(Company, Company.id == company_id)
        page: Page = CompanyService.get_organizations_with_rules(str(company_id), ListRules.from_params(request.args))
        organizations = OrganizationSchema().dump(page.results, many=True)
        return make_response({"entities": organizations, "total": page.total})


class OrganizationById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = (PERM_USER,)

    @no_body_allowed
    def get(self, organization_id: UUID) -> Response:
        """Get Organization by ID
        ---
        tags: ["Organization"]
        operationId: GetOrganizationById
        description: Retrieves a single organization by its ID.
        security:
        parameters:
          - in: path
            name: organization_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - organization returned.
            content:
              application/json:
                schema: OrganizationSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Organization not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        organization = self.get_entity_or_fail(Organization, Organization.id == organization_id)
        return make_response(OrganizationSchema().dump(organization))
