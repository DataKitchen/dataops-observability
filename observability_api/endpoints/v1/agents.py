__all__ = ["Agents"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Project
from common.entity_services import agent_service
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import AgentSchema

LOG = logging.getLogger(__name__)


class Agents(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Agents LIST
        ---
        tags: ["Agent"]
        description: Lists all agents for the project using the specified project ID.
        operationId: ListAgents
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
            description: The sort order for the agent list. The sort is applied to the list before pagination.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only agent keys or tool names with
                         a partial or full match to the query will be listed.
        responses:
          200:
            description: Request successful - agent list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/AgentSchema'
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
        _ = self.get_entity_or_fail(Project, Project.id == project_id)
        page: Page = agent_service.get_agents_with_rules(str(project_id), ListRules.from_params(request.args))
        agents = AgentSchema().dump(page.results, many=True)
        return make_response({"entities": agents, "total": page.total})
