__all__ = ["ProjectAlerts"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Project
from common.entity_services import ProjectService
from common.entity_services.helpers import ListRules, SortOrder
from common.entity_services.helpers.filter_rules import AlertFilters
from observability_api.endpoints.entity_view import BaseEntityView

LOG = logging.getLogger(__name__)


class ProjectAlerts(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Get alerts by project ID
        ---
        tags: ["Project", "Alerts"]
        description: Retrieves alerts by project_id.
        operationId: ProjectAlerts
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: project_id
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
            name: sort
            schema:
              type: string
              default: ASC
              enum:
                - ASC
                - DESC
            description: The sort order for the alerts list. The sort is applied to the list before pagination.
          - in: query
            name: count
            schema:
              type: integer
              default: 10
            description: The number of results to display per page.
          - in: query
            name: instance_id
            description: Optional. If specified, the results will be limited to alerts with one of the specified instance IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: run_id
            description: Optional. If specified, the results will be limited to alerts with one of the specified run IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: run_key
            description: Optional. If specified, the results will be limited to alerts with one of the specified run keys.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: level
            description: Optional. If specified, the results will be limited to alerts with one of the specified levels.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: type
            description: Optional. If specified, the results will be limited to alerts with one of the specified alert types.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: component_id
            description: Optional. If specified, the results will be limited to alerts with one of the specified
                         component IDs. In case of run alerts, the component ID is the run's pipeline ID.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: date_range_start
            description: Optional. An ISO8601 datetime. If specified, The result will only include alerts created on
                         the same or after the given datetime. May be specified with date_range_end to create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: date_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only contain alerts created on
                         before the given datetime. May be specified with date_range_start to create a range.
            schema:
              type: string
              format: date
            required: false
        responses:
          200:
            description: Request successful - alerts returned.
            content:
              application/json:
                schema: UIAlertSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
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
        _ = self.get_entity_or_fail(Project, Project.id == project_id)
        rules = ListRules.from_params(request.args)
        if "sort" not in request.args:
            rules.sort = SortOrder.DESC
        page = ProjectService.get_alerts_with_rules(str(project_id), rules, AlertFilters.from_params(request.args))
        return make_response({"entities": page.results, "total": page.total})
