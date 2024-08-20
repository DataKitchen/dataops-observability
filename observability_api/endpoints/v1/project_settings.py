__all__ = ["ProjectAlertsSettings"]

from typing import Optional, cast, Any
from uuid import UUID

from flask import Response, make_response
from marshmallow import Schema, ValidationError
from marshmallow.fields import Nested, Field, Int
from marshmallow.validate import Range

from common.actions.action import ActionTemplateRequired, ActionException
from common.actions.action_factory import action_factory
from common.api.base_view import PERM_PROJECT, PERM_USER, Permission
from common.api.request_parsing import no_body_allowed
from common.constants import MAX_AGENT_CHECK_INTERVAL_SECONDS, MIN_AGENT_CHECK_INTERVAL_SECONDS
from common.entities import Project
from common.entity_services import ProjectService
from common.exceptions.service import MultipleActionsFound
from common.schemas.action_schemas import ActionSchema
from observability_api.endpoints.entity_view import BaseEntityView


class ProjectAlertsSettings(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = (PERM_USER, PERM_PROJECT)

    _project: Optional[Project]

    def get_request_schema(self) -> Schema:
        return cast(Schema, Schema.from_dict(self.get_fields(), name=f"{self.__class__.__name__}Schema")())

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """Get the alert settings of a given project.
        ---
        tags: ["Project"]
        operationId: GetProjectAlertsSettings
        description: Retrieves the alerts settings of a given project.
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
            description: Request successful - settings returned.
            content:
              application/json:
                schema: ProjectAlertsSettingsSchema
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
        self._project = self.get_entity_or_fail(Project, Project.id == project_id)
        return make_response(self.get_request_schema().dump(self._project))

    def patch(self, project_id: UUID) -> Response:
        """Update the alert settings of a given project.
        ---
        tags: ["Project"]
        description: Updates the alert settings of a given project.
        operationId: PatchProjectAlertsSettings
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
          description: The update data for the project alert settings.
          required: true
        responses:
          200:
            description: Request successful - project settings updated.
            content:
              application/json:
                schema: ProjectAlertsSettingsSchema
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
        self._project = self.get_entity_or_fail(Project, Project.id == project_id)
        schema = self.get_request_schema()
        self.patch_entity(schema=schema, entity=self._project)
        self.save_entity_or_fail(self._project)
        return make_response(schema.dump(self._project))

    def get_fields(self) -> dict[str, Field | type]:
        def _validate_actions(actions: list[dict[str, Any]]) -> None:
            template_actions = ProjectService.get_template_actions(
                cast(Project, self._project), [a["action_impl"] for a in actions]
            )
            error_messages = []
            for idx, action in enumerate(actions):
                try:
                    action_factory(
                        action["action_impl"],
                        action.get("action_args", {}),
                        template_actions.get(action["action_impl"], None),
                    )
                except ActionTemplateRequired:
                    error_messages.append(
                        f"Action {idx} ({action['action_impl']}) is lacking arguments or misconfigured"
                    )
                except (MultipleActionsFound, ActionException, ValueError):
                    error_messages.append(
                        f"Action {idx} ({action['action_impl']}) is misconfigured and can not be used"
                    )
            if error_messages:
                raise ValidationError(error_messages)

        fields: dict[str, Field | type] = {
            "agent_check_interval": Int(
                required=True,
                validate=Range(min=MIN_AGENT_CHECK_INTERVAL_SECONDS, max=MAX_AGENT_CHECK_INTERVAL_SECONDS),
            ),
            "actions": Nested(
                ActionSchema(many=True),
                attribute="alert_actions",
                required=True,
                dump_default=[],
                validate=_validate_actions,
            ),
        }
        return fields
