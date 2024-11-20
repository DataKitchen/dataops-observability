import base64
import logging
from http import HTTPStatus
from typing import cast

from flask import Response, make_response, request
from werkzeug.exceptions import Forbidden, Unauthorized

from common.api.base_view import BaseView
from common.api.flask_ext.authentication import JWTAuth
from common.api.flask_ext.authentication.common import get_domain
from common.api.request_parsing import no_body_allowed
from common.auth.keys.lib import hash_value
from common.entities import AuthProvider, User

LOG = logging.getLogger(__name__)


class Logout(BaseView):
    PERMISSION_REQUIREMENTS = ()

    @no_body_allowed
    def get(self) -> Response:
        """
        Logout endpoint
        ---
        tags: ["Auth"]
        description: Revokes the access token provided by the SSO Authority when enabled. This endpoint is
                    not intended for use by end users.
        operationId: GetLogout
        responses:
            204:
                description: Request successful - Token revoked.
            400:
                description: Request bodies are not supported by this endpoint.
            500:
                description: Unverified error. Consult the response body for more details.
                content:
                    application/json:
                        schema: HTTPErrorSchema
        """
        JWTAuth.log_user_out()
        return make_response("", HTTPStatus.NO_CONTENT)


class BasicLogin(BaseView):
    PERMISSION_REQUIREMENTS = ()

    @no_body_allowed
    def get(self) -> dict[str, str]:
        """
        Login to the observability tool using basic authentication method.

        ---
        tags: ["Auth"]
        description: Login to the observability tool using basic authentication method. A JWT token that should be used
                     to authenticate subsequent requests will be returned when the endpoint succeeds.  This
                     endpoint is not intended for use by end users.
        operationId: GetAuthLogin
        security:
          - Basic: []
        responses:
          204:
            description: Request successful - User logged in.
          401:
            description: Invalid username or password.
            content:
              application/json:
                schema: HTTPErrorSchema
          403:
            description: Inactive user is not allowed to log in.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        auth = request.authorization
        if auth is None or auth.type != "basic":
            LOG.warning(str(auth))
            raise Unauthorized("Missing authorization headers.")

        # Disable when auth provider is configured
        if AuthProvider.select().where(AuthProvider.domain == get_domain()).exists():
            LOG.warning("User/password login attempted when an AuthProvider is configured.")
            raise Unauthorized("Invalid username or password.")

        try:
            user = User.select().where(User.username == auth.username).get()
        except User.DoesNotExist as user_dne:
            LOG.warning("No user found with '%s' username", auth.username)
            raise Unauthorized("Invalid username or password.") from user_dne
        encoded_pw = base64.b64encode(hash_value(value=cast(str, auth.password), salt=user.salt)).decode()
        if encoded_pw != user.password:
            LOG.warning("The provided password did not match for user '%s'", auth.username)
            raise Unauthorized("Invalid username or password.")

        if not user.active:
            LOG.warning("Inactive user '%s' attempted to log in", user)
            raise Forbidden("User is not active")

        session_token = JWTAuth.log_user_in(user)
        return {"token": session_token}
