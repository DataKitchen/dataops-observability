__all__ = ["get_domain", "BaseAuthPlugin", "validate_authentication"]
import logging
import re
from urllib.parse import urlparse

from flask import current_app, g, request
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Unauthorized

from common.entities import User

from ..base_extension import BaseExtension

LOG = logging.getLogger(__name__)


class BaseAuthPlugin(BaseExtension):
    header_name: str = NotImplemented
    header_prefix: str | None = None

    @classmethod
    def get_header_data(cls) -> str | None:
        auth_data = request.headers.get(cls.header_name, None)
        if auth_data and cls.header_prefix:
            if match := re.match(rf"^{cls.header_prefix}\s+(.*)\s*$", auth_data):
                auth_data = match.group(1)
            else:
                auth_data = None
        return auth_data

    @classmethod
    def pre_request_auth(cls) -> None:
        raise NotImplementedError

    def init_app(self) -> None:
        self.add_before_request_func(self.pre_request_auth)
        self.add_or_move_before_request_func(validate_authentication)


def get_domain() -> str:
    """
    Extract the source domain from the request. Uses Origin header, falling back to Host.

    The format for the host header is simply `domain.name:port` (with port optional) whereas the Origin includes the
    scheme portion and is formatted `scheme://domain.name:port` (once again with port optional). request.url_root is
    provided by flask and also includes the URL scheme. Because of this, urlparse is needed for the Origin header and
    request.url_root, but not for the Host header.
    """
    if (source_url := request.headers.get("Origin")) is not None:
        try:
            netloc = urlparse(source_url).netloc
        except Exception as e:
            raise ValueError(f"Malformed `Origin` header: {source_url}") from e
    else:
        LOG.warning("`Origin` header missing. Falling back to `Host` header")
        if netloc := request.headers.get("Host", ""):
            try:
                urlparse(f"fake://{netloc}")
            except Exception as e:
                raise ValueError(f"Malformed `Host` header: {netloc}") from e
        else:
            LOG.warning("`Host` header missing. Falling back to flasks `url_root` request attribute")
            netloc = urlparse(request.url_root).netloc

    # Try parsing a fake url based off of the netloc value; if the netloc of the parsed result is unchanged then the
    # value is a valid domain.
    if (parsed := urlparse(f"fake://{netloc}")) and parsed.netloc != netloc:
        raise ValueError(f"Extracted domain is malformed: `{netloc}`")
    return netloc.rsplit(":", 1)[0]  # Lop off the port if present


def validate_authentication() -> None:
    """
    Validate that the request is authenticated.

    This function can be used by plugins to raise an error if the application is not properly authenticated. Plugins
    are expected to add either a `user` attribute to the application context (flask.g) or a `service_name` attribute.
    If one of these attributes is not present, 401 NotAuthorized is raised.

    This function honors the `AUTHENTICATION_EXCLUDED_ROUTES` setting value and does not raise a 401 NotAuthorized
    error for these endpoints.

    A boolean attribute `is_authenticated` is added to the application context for the current request. It defaults to
    False but will be set to True if the `user` attribute or ``service_name`` attribute are valid.
    """
    g.is_authenticated = False
    if request.endpoint is None:
        # The `request.endpoint` value is None when no url match occurred. This will eventually generate a 404, but it
        # is bad practice to skip authentication verification for any reason, even if you're confident it won't matter
        # further along the call stack. Simply put, NEVER assume it's safe to skip authentication validation unless
        # you're dealing with an endpoint that you are intentionally excluding from authentication. i.e. a login page
        # or health probes.
        raise NotFound()

    if getattr(g, "user", None) is not None and getattr(g, "project", None) is not None:
        raise BadRequest("Only one authentication method is allowed at a time.")

    if getattr(g, "auth_plugin", None):
        raise BadRequest("It was not possible to determine the login method")

    # If the endpoint is excluded from authentication validation then it's safe to return
    if request.endpoint in current_app.config.get("AUTHENTICATION_EXCLUDED_ROUTES", ()):
        return None

    # If the user attribute is set, check that it is a valid User instance
    if isinstance((user := getattr(g, "user", None)), User) is True:
        if g.user.active:
            g.is_authenticated = True
            LOG.debug("User %s is successfully authenticated.", user)
            return None  # Authentication was successful
        else:
            LOG.info("User with id %s is not active", g.user.id)
            raise Forbidden("User is not active")

    # If the service name attribute is present, make sure it matches the current application service name
    if (allowed_services := getattr(g, "allowed_services", None)) and (
        project := getattr(g, "project", None)
    ) is not None:
        if (expected_service_name := current_app.config.get("SERVICE_NAME")) in allowed_services:
            if project.active:
                LOG.debug("Service Account authentication for service %s succeeded.", expected_service_name)
                g.is_authenticated = True
                return None
            else:
                LOG.warning("Service account key is for inactive project `%s`", project)
        else:
            LOG.warning(
                "Service account key is for services %s but required `%s`",
                allowed_services,
                expected_service_name,
            )

    LOG.debug("Unauthenticated attempt to access endpoint %s: %s ", request.endpoint, request.full_path)
    raise Unauthorized()
