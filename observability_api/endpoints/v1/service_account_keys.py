__all__ = ["ServiceAccountKeys", "ServiceAccountKeyById"]

import logging
from http import HTTPStatus
from uuid import UUID

from flask import Response, make_response, request
from peewee import IntegrityError
from werkzeug.exceptions import Conflict

from common.api.base_view import PERM_USER
from common.api.request_parsing import no_body_allowed
from common.auth.keys.service_key import generate_key
from common.entities import DB, Project, ServiceAccountKey
from common.entity_services import ServiceAccountKeyService
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import (
    ServiceAccountKeyCreateSchema,
    ServiceAccountKeySchema,
    ServiceAccountKeyTokenSchema,
)

LOG = logging.getLogger(__name__)


class ServiceAccountKeys(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER,)

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """Service Account Key LIST
        ---
        tags: ["ServiceAccountKey"]
        description: Lists service account keys in the project.
        operationId: ListServiceAccountKeys
        security:
        parameters:
          - in: path
            name: project_id
            description: The ID of the project that the service account key will be created under.
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
            description: The sort order for the key list. The sort is applied to the list before pagination.
          - in: query
            name: search
            schema:
              type: string
            description: Filters the returned list by searching the key name and description.
        responses:
          200:
            description: Request successful - key list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/ServiceAccountKeySchema'
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
        project = self.get_entity_or_fail(Project, Project.id == project_id)
        page: Page = ServiceAccountKeyService.list_with_rules(
            project=project, rules=ListRules.from_params(request.args)
        )
        sa_keys = ServiceAccountKeySchema().dump(page.results, many=True)
        return make_response({"entities": sa_keys, "total": page.total})

    def post(self, project_id: UUID) -> Response:
        """Service Account Key CREATE
        ---
        tags: ["ServiceAccountKey"]
        operationId: PostServiceAccountKey
        description: Creates a new service account key for a specified project.
        security:
        parameters:
          - in: path
            name: project_id
            description: The ID of the project that the service account key will be created under.
            schema:
              type: string
            required: true
        requestBody:
          description: The data required for the new service account key.
          required: true
          content:
            application/json:
              schema: ServiceAccountKeyCreateSchema
        responses:
          201:
            description: Request successful - new service account key created.
            content:
              application/json:
                schema: ServiceAccountKeyTokenSchema
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
        req = ServiceAccountKeyCreateSchema().load(self.request_body)
        allowed_services = [service.name for service in req["allowed_services"]]
        try:
            sa_key = generate_key(
                allowed_services=allowed_services,
                project=project.id,
                name=req["name"],
                description=req.get("description"),
                expiration_days=req["expires_after_days"],
            )
        except IntegrityError:
            raise Conflict("Service Account Key with name `{req['name']}` already exists in project `{project.name}`")

        res = ServiceAccountKeyTokenSchema().dump(sa_key)
        return make_response(res, HTTPStatus.CREATED)


class ServiceAccountKeyById(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER,)

    @no_body_allowed
    def delete(self, key_id: UUID) -> Response:
        """Delete a Service Account Key by ID
        ---
        tags: ["ServiceAccountKey"]
        operationId: DeleteServiceAccountKeyById
        description: Permanently deletes a service account key.
        security:
        parameters:
          - in: path
            name: key_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - service account key deleted.
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
        sa_key = self.get_entity_or_fail(ServiceAccountKey, ServiceAccountKey.id == key_id)
        with DB.atomic():
            sa_key.delete_instance()
        return make_response("", HTTPStatus.NO_CONTENT)
