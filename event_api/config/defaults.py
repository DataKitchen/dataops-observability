"""
Events API default settings.

Settings here may be overridden by settings in development, test, production, etc...
"""

import os
from typing import Optional

# Flask specific settings: https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values
from common.entities import Service

PROPAGATE_EXCEPTIONS: Optional[bool] = None
SERVER_NAME: Optional[str] = os.environ.get("EVENTS_API_HOSTNAME")  # Use flask defaults if none set
USE_X_SENDFILE: bool = False  # If we serve files enable this in production settings when webserver support configured

# Application settings
API_PREFIX: str = "events"
"""Prefix for all API endpoints."""

AUTHENTICATION_EXCLUDED_ROUTES: tuple[str, ...] = ("health.readyz", "health.livez")
"""Flask route names which do not need an authenticated JWT or API key."""

SERVICE_NAME: str = Service.EVENTS_API.name
"""Name given to the service; used for validating service account keys."""

MAX_REQUEST_BODY_SIZE: int = 100 * 1024  # 100KB
"""Event HTTP request max body size in bytes."""
