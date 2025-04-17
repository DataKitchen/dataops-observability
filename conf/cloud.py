import json
import os

from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectingPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


CORS_DOMAINS: list[str] = os.environ.get("CORS_DOMAINS", "*").split(",")

DATABASE: dict[str, object] = {
    "name": "datakitchen",
    "engine": ReconnectingPooledMySQLDatabase,
    "user": os.environ.get("DB_USER"),
    "passwd": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "max_connections": 32,
    "stale_timeout": 300,
}
"""Settings for connecting to the production database instance."""


# We accept a dictionary so we can override advanced Kafka settings easily through environment variables
KAFKA_CONNECTION_PARAMS: dict[str, object] = json.loads(os.environ.get("KAFKA_CONNECTION_PARAMS", "{}"))
"""Settings to connect to Kafka."""


SMTP: dict[str, object] = {
    "username": os.environ.get("SMTP_USER"),
    "password": os.environ.get("SMTP_PASSWORD"),
    "endpoint": os.environ.get("SMTP_ENDPOINT"),
    "port": int(os.environ.get("SMTP_PORT", 465)),
    "from_address": os.environ.get("SMTP_FROM_ADDRESS"),
}
"""Settings for connecting to the SMTP email server."""
