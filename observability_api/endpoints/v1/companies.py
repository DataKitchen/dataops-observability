__all__ = ["CompanyById"]

import logging
from uuid import UUID

from flask import Response, make_response

from common.api.base_view import PERM_USER
from common.api.request_parsing import no_body_allowed
from common.entities import Company
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import CompanySchema

LOG = logging.getLogger(__name__)


class CompanyById(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER,)

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
