__all__ = ["DatabaseConnection"]

import logging
from typing import Any

from flask import current_app, request

from common.entities import DB
from conf import init_db

from .base_extension import BaseExtension

LOG = logging.getLogger(__name__)


class DatabaseConnection(BaseExtension):
    """
    Manage a database connection.

    This makes use of configuration values. The `Config` plugin must be added to the Flask app BEFORE this plugin.
    """

    @staticmethod
    def db_connect() -> None:
        if request.endpoint not in current_app.config.get("DB_EXCLUDED_ROUTES", ()):
            init_db()  # Sets up database and establishes connection

    @staticmethod
    def db_disconnect(exc: Any) -> None:
        """Close database connection when the application context is torn down."""
        try:
            if DB.obj is not None:
                DB.close()
        except Exception:
            LOG.exception("Error closing connection to database")

    def init_app(self) -> None:
        if self.app is not None:
            self.add_before_request_func(DatabaseConnection.db_connect)
            self.app.teardown_request(DatabaseConnection.db_disconnect)
