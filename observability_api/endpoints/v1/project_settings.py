__all__ = ["ProjectAlertsSettings"]

from uuid import UUID

from flask import Response, make_response
from marshmallow import Schema
from marshmallow.fields import Nested, Field, Int


from common.api.base_view import PERM_PROJECT, PERM_USER, Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Project
from common.schemas.action_schemas import ActionSchema
from observability_api.endpoints.entity_view import BaseEntityView


class ProjectSettingByID(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = (PERM_USER, PERM_PROJECT)

    fields: dict[str, Field | type] = NotImplemented

    @property
    def request_schema_class(self) -> type:
        return Schema.from_dict(self.fields, name=f"{self.__class__.__name__}Schema")

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """Get Project by ID
        ---
        tags: ["Project"]
        operationId: GetProjectById
        description: Retrieves the settings for a single namespace under project.
        security:
          - SAKey: []
        parameters:
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
        return make_response(self.request_schema_class().dump(project))

    def patch(self, project_id: UUID) -> Response:
        """Update a nespaced Project setting by project ID
        ---
        tags: ["Project"]
        description: Updates settings for a single namespace under project.
        operationId: PatchProjectSettingById
        security:
          - APIKey: []
          - SAKey: []
        parameters:
          - in: path
            name: project_id
            schema:
              type: string
            required: true
        requestBody:
          description: The update data for the project.
          required: true
        responses:
          200:
            description: Request successful - project updated.
            content:
              application/json:
                schema: ProjectSchema
          400:
            description: There is invalid or missing data in the request body.
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
        self.patch_entity(schema=self.request_schema_class(), entity=project)
        self.save_entity_or_fail(project)
        return make_response(self.request_schema_class().dump(project))


class ProjectAlertsSettings(ProjectSettingByID):
    fields = {
        "agent_check_interval": Int(attribute="agent_status_check_interval", required=True),
        "actions": Nested(ActionSchema(many=True), attribute="alert_actions", required=True, dump_default=[]),
    }
