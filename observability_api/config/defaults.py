"""
Observability API default settings.

Settings here may be overridden by settings in development, test, production, etc...
"""

import os
from datetime import timedelta
from typing import Optional

# Flask specific settings: https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values
from common.entities import Service

PROPAGATE_EXCEPTIONS: Optional[bool] = None
SERVER_NAME: Optional[str] = os.environ.get("OBSERVABILITY_API_HOSTNAME", None)  # Use flask defaults if none set
USE_X_SENDFILE: bool = False  # If we serve files enable this in production settings when webserver support configured

# Application settings
API_PREFIX: str = "observability"
"""Prefix for all API endpoints."""

DB_EXCLUDED_ROUTES: tuple[str, ...] = ("health.livez",)
"""Flask route names which can be omitted from DB setup/teardown."""

AUTHENTICATION_EXCLUDED_ROUTES: tuple[str, ...] = (
    "health.readyz",
    "health.livez",
    "v1.auth-basic-login",
    "v1.auth-sso-login",
)
"""Flask route names which do not need an authenticated JWT or API key."""

OAUTHLIB_INSECURE_TRANSPORT: bool = False
"""Determines whether to allow single-sign-on flow on an insecure connection (not https)."""

SERVICE_NAME: str = Service.OBSERVABILITY_API.name
"""Name given to the service; used for validating service account keys."""

DEFAULT_JWT_EXPIRATION_SECONDS: float = timedelta(hours=24).total_seconds()
"""Default expiration period for the JWT tokens."""
