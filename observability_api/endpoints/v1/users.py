import logging
from uuid import UUID

from flask import Response, make_response, request
from peewee import DoesNotExist
from werkzeug.exceptions import Forbidden, NotFound

from common.api.base_view import PERM_USER, PERM_USER_ADMIN, BaseView
from common.api.request_parsing import no_body_allowed
from common.constants import ADMIN_ROLE
from common.entities import User
from common.entity_services import UserService
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas.user_schemas import UserSchema

LOG = logging.getLogger(__name__)


class Users(BaseView):
    PERMISSION_REQUIREMENTS = (PERM_USER_ADMIN,)

    @no_body_allowed
    def get(self) -> Response:
        """
        User LIST
        ---
        tags: ["User"]
        description: Lists all users in the system, filtered by optional parameters.
        operationId: ListUsers
        security:
        parameters:
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
            description: The sort order for the user list. The sort is applied to the list before pagination.
          - in: query
            name: primary_company
            schema:
              type: string
            description: Optional. A company ID for filtering the user list.
          - in: query
            name: name
            schema:
              type: string
            description: Optional. A substring for filtering the user list to partial user name matches.
        responses:
          200:
            description: Request successful - user list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/UserSchema'
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
        company_id = request.args.get("primary_company")
        page: Page = UserService.list_with_rules(
            ListRules.from_params(request.args), company_id=company_id, name_filter=request.args.get("name")
        )

        users = UserSchema().dump(page.results, many=True)
        return make_response({"entities": users, "total": page.total})


class UserById(BaseEntityView):
    PERMISSION_REQUIREMENTS = (PERM_USER,)

    @no_body_allowed
    def get(self, user_id: UUID) -> Response:
        """
        Get User by ID
        ---
        tags: ["User"]
        description: Retrieves a single user by its ID.
        operationId: GetUserById
        security:
        parameters:
          - in: path
            name: user_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - user list returned.
            content:
              application/json:
                schema: UserSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: User not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        if not self.user or (ADMIN_ROLE not in self.user_roles and self.user.id != user_id):
            raise Forbidden()

        try:
            user = User.get_by_id(user_id)
        except DoesNotExist as dne:
            raise NotFound(f"No User exists with the ID '{user_id}") from dne
        return make_response(UserSchema().dump(user))
