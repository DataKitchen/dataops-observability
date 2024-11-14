import logging
from uuid import UUID

from flask import Response, make_response, request
from werkzeug.exceptions import Forbidden

from common.api.base_view import PERM_USER, Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Project
from common.entity_services import UpcomingInstanceService
from common.entity_services.helpers import ListRules, UpcomingInstanceFilters
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import UpcomingInstanceSchema

LOG = logging.getLogger(__name__)


class UpcomingInstances(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Upcoming Instance LIST
        ---
        tags: ["UpcomingInstance"]
        description: List upcoming instances of a project.
        operationId: ListUpcomingInstances
        security:
          - SAKey: []
        parameters:
          - in: path
            name: project_id
            description: the ID of the project being queried.
            schema:
              type: string
            required: true
          - in: query
            name: journey_id
            description: Optional. Specifies which journeys to include by their ID. All journeys are selected if
                         unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: journey_name
            description: Optional. If specified, the results will be limited to instances with the journeys named.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: start_range
            description: An ISO8601 datetime. If specified, The result will only include upcoming instances
                         with a expected start or end time equal or past the given datetime.
            schema:
              type: string
              format: date
            required: true
          - in: query
            name: end_range
            description: Optional. An ISO8601 datetime. If specified, the result will only contain instances with a
                         expected start or end time before the given datetime.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: count
            schema:
              type: integer
              default: 10
            description: The number of results to display.
        responses:
          200:
            description: Request successful - Instance list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/UpcomingInstanceSchema'
          404:
            description: Project not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        self.get_entity_or_fail(Project, Project.id == project_id)
        upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
            ListRules.from_params(request.args),
            UpcomingInstanceFilters.from_params(request.args),
            project_id,
        )
        return make_response({"entities": UpcomingInstanceSchema().dump(upcoming_instances, many=True)})


class CompanyUpcomingInstances(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = (PERM_USER,)

    @no_body_allowed
    def get(self) -> Response:
        """
        Company Upcoming Instance LIST
        ---
        tags: ["UpcomingInstance"]
        description: List upcoming instances of a company.
        operationId: ListCompanyUpcomingInstances
        security:
        parameters:
          - in: query
            name: project_id
            description: Optional. Specifies the project IDs to include. All projects are selected if unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: journey_id
            description: Optional. Specifies which journeys to include by their ID. All journeys are selected if
                         unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: journey_name
            description: Optional. If specified, the results will be limited to instances with the journeys named.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: start_range
            description: An ISO8601 datetime. If specified, The result will only include upcoming instances
                         with a expected start or end time equal or past the given datetime.
            schema:
              type: string
              format: date
            required: true
          - in: query
            name: end_range
            description: Optional. An ISO8601 datetime. If specified, the result will only contain instances with a
                         expected start or end time before the given datetime.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: count
            schema:
              type: integer
              default: 10
            description: The number of results to display.
        responses:
          200:
            description: Request successful - Instance list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/UpcomingInstanceSchema'
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        if not self.user:
            raise Forbidden()
        company_id = self.user.primary_company.id

        upcoming_instances = UpcomingInstanceService.get_upcoming_instances_with_rules(
            ListRules.from_params(request.args),
            UpcomingInstanceFilters.from_params(request.args),
            company_id=company_id,
        )
        return make_response({"entities": UpcomingInstanceSchema().dump(upcoming_instances, many=True)})
