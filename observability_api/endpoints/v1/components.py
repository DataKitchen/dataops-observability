__all__ = ["Components", "ComponentById", "JourneyComponents"]

import logging
from http import HTTPStatus
from uuid import UUID

from flask import Response, make_response, request
from werkzeug.exceptions import NotFound

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Component, Journey, Project
from common.entity_services import JourneyService, ProjectService
from common.entity_services.helpers import ComponentFilters, ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import ComponentSchema

LOG = logging.getLogger(__name__)


class Components(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """Component LIST by project
        ---
        tags: ["Component"]
        description: Lists all components for the project using the specified project ID.
        operationId: ListComponents
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
            name: component_type
            schema:
              type: array
              items:
                type: string
            description: Optional. If specified, the results will be limited to components with the listed types.
          - in: query
            name: tool
            schema:
              type: array
              items:
                type: string
            description: Optional. If specified, the results will be limited to components with the listed tools.
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
            description: The sort order for the component list. The sort is applied to the list before pagination.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only component keys with a partial or
                         full match to the query will be listed.
        responses:
          200:
            description: Request successful - component list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/ComponentSchema'
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
        page: Page = ProjectService.get_components_with_rules(
            self.get_entity_or_fail(Project, Project.id == project_id).id,
            ListRules.from_params(request.args),
            ComponentFilters.from_params(request.args),
        )
        components = ComponentSchema().dump(page.results, many=True)
        return make_response({"entities": components, "total": page.total})


class ComponentById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, component_id: UUID) -> Response:
        """Get component by ID
        ---
        tags: ["Component"]
        operationId: GetComponentById
        description: Retrieves a single component by its ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: component_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - component returned.
            content:
              application/json:
                schema: ComponentSchema
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
        component = self.get_entity_or_fail(Component, Component.id == component_id)
        return make_response(ComponentSchema().dump(component))

    @no_body_allowed
    def delete(self, component_id: UUID) -> Response:
        """Delete a Component by ID
        ---
        tags: ["Component"]
        operationId: DeleteComponentById
        description: Permanently deletes a single component by its ID including all the associated runs and stored events.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: component_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - component deleted.
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
            self.get_entity_or_fail(Component, Component.id == component_id).delete_instance()
        except NotFound:
            pass
        return make_response("", HTTPStatus.NO_CONTENT)


class JourneyComponents(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, journey_id: UUID) -> Response:
        """Component LIST by journey
        ---
        tags: ["Component"]
        description: Lists all components for the journey using the specified journey ID.
        operationId: ListComponentsByJourney
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            description: the ID of the journey being queried.
            schema:
              type: string
            required: true
          - in: query
            name: component_type
            schema:
              type: array
              items:
                type: string
            description: Optional. If specified, the results will be limited to components with the listed types.
          - in: query
            name: tool
            schema:
              type: array
              items:
                type: string
            description: Optional. If specified, the results will be limited to components with the listed tools.
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
            description: The sort order for the component list. The sort is applied to the list before pagination.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only component keys with a partial or
                         full match to the query will be listed.
        responses:
          200:
            description: Request successful - component list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/ComponentSchema'
                    total:
                      type: integer
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
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
        journey = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        page: Page = JourneyService.get_components_with_rules(
            str(journey.id), ListRules.from_params(request.args), ComponentFilters.from_params(request.args)
        )
        components = ComponentSchema().dump(page.results, many=True)
        return make_response({"entities": components, "total": page.total})
