"""
Heartbeat Service default settings.

Settings here may be overridden by settings in development, test, production, etc...
"""
import os
from typing import Optional

# Flask specific settings: https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values
from common.entities import Service

PROPAGATE_EXCEPTIONS: Optional[bool] = None
SERVER_NAME: str = os.environ.get("AGENT_API_HOSTNAME", None)  # Use flask defaults if none set
USE_X_SENDFILE: bool = False  # If we serve files enable this in production settings when webserver support configured

# Application settings
API_PREFIX: str = "agent"
"""Prefix for all API endpoints."""

AUTHENTICATION_EXCLUDED_ROUTES: tuple[str, ...] = ("health.readyz", "health.livez")
"""Flask route names which do not need an authenticated JWT or API key."""

SERVICE_NAME: str = Service.AGENT_API.name
"""Name given to the service; used for validating service account keys."""

MAX_REQUEST_BODY_SIZE: int = 102_400  # 100KB (100 * 1024)
"""HTTP request max body size in bytes."""
