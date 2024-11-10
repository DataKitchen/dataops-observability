__all__ = ["Projects", "ProjectById", "ProjectEvents"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import PERM_PROJECT, PERM_USER, Permission
from common.api.request_parsing import no_body_allowed
from common.entities import DB, EventEntity, Organization, Project  # noqa: F401
from common.entity_services import OrganizationService
from common.entity_services.event_service import EventService
from common.entity_services.helpers import ListRules, Page, ProjectEventFilters
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas.event_schemas import EventResponseSchema
from observability_api.schemas.project_schemas import ProjectSchema

LOG = logging.getLogger(__name__)


class Projects(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER,)

    @no_body_allowed
    def get(self, organization_id: UUID) -> Response:
        """
        Project LIST
        ---
        tags: ["Project"]
        description: Lists all projects in an organization using the specified organization ID.
        operationId: ListProjects
        parameters:
          - in: path
            name: organization_id
            description: The ID of organization being queried for projects.
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
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only project names with a partial or
                         full match to the query will be listed.
        responses:
          200:
            description: Request successful - project list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/ProjectSchema'
                    total:
                      type: integer
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
        _ = self.get_entity_or_fail(Organization, Organization.id == organization_id)
        page: Page = OrganizationService.get_projects_with_rules(
            str(organization_id), ListRules.from_params(request.args)
        )
        projects = ProjectSchema().dump(page.results, many=True)
        return make_response({"entities": projects, "total": page.total})


class ProjectById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = (PERM_USER, PERM_PROJECT)

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Get Project by ID
        ---
        tags: ["Project"]
        operationId: GetProjectById
        description: Retrieves a single project by its ID.
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: project_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - project returned.
            content:
              application/json:
                schema: ProjectSchema
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
        project = self.get_entity_or_fail(Project, Project.id == project_id)
        return make_response(ProjectSchema().dump(project))


class ProjectEvents(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Get events by Project ID
        ---
        tags: ["Project", "Events"]
        description: Retrieves events by project_id.
        security:
          - SAKey: []
        operationId: ProjectEvents
        parameters:
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
            description: The sort order for the event list. The sort is applied to the list before pagination.
          - in: query
            name: count
            schema:
              type: integer
              default: 10
            description: The number of results to display per page.
          - in: query
            name: event_id
            description: Optional. If specified, the results will be limited to events with the given IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: journey_id
            description: Optional. If specified, the results will be limited to events with one of the given journey IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: component_id
            description: Optional. If specified, the results will be limited to events with one of the given component IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: run_id
            description: Optional. If specified, the results will be limited to events with one of the specified run IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: instance_id
            description: Optional. If specified, the results will be limited to events with one of the specified instance IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: task_id
            description: Optional. If specified, the results will be limited to events with one of the specified task IDs.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: date_range_start
            description: Optional. An ISO8601 datetime. If specified, The result will only include events with an
                         event_timestamp field equal or past the given datetime. May be specified with date_range_end
                         to create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: date_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only contain events with an
                         event_timestamp field before the given datetime. May be specified with date_range_start to create
                         a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: event_type
            description: Optional. If specified, the results will be limited to events with one of the specified event
                         types.
            schema:
              type: array
              items:
                type: string
                enum:
                  - BATCH_PIPELINE_STATUS
                  - DATASET_OPERATION
                  - MESSAGE_LOG
                  - METRIC_LOG
                  - TEST_OUTCOMES
        responses:
          200:
            description: Request successful - project event details returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/EventResponseSchema'
                    total:
                      type: integer
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
        self.get_entity_or_fail(Project, Project.id == project_id)
        event_filters = ProjectEventFilters.from_params(request.args, project_ids=[project_id])
        page: Page[EventEntity] = EventService.get_events_with_rules(
            rules=ListRules.from_params(request.args), filters=event_filters
        )
        return make_response({"entities": EventResponseSchema().dump(page.results, many=True), "total": page.total})
