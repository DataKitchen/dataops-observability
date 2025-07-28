import os

from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectingPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


CORS_DOMAINS: list[str] = os.environ.get("CORS_DOMAINS", "*").split(",")

DATABASE: dict[str, object] = {
    "name": "datakitchen",
    "engine": ReconnectingPooledMySQLDatabase,
    "user": os.environ.get("MYSQL_USER"),
    "passwd": os.environ.get("MYSQL_PASSWORD"),
    "host": os.environ.get("MYSQL_SERVICE_HOST"),
    "port": int(os.environ.get("MYSQL_SERVICE_PORT", 3306)),
    "max_connections": 32,
    "stale_timeout": 300,
}
"""Settings for connecting to the development database instance."""


KAFKA_CONNECTION_PARAMS: dict[str, object] = {
    "bootstrap.servers": f"{os.environ.get('KAFKA_SERVICE_HOST')}:{os.environ.get('KAFKA_SERVICE_PORT')}",
}
"""Settings to connect to Kafka."""

RULE_REFRESH_SECONDS = 1
"""Number of seconds to cache rules in rules engine"""


SMTP: dict[str, object] = {
    "username": os.environ.get("SMTP_USER"),
    "password": os.environ.get("SMTP_PASSWORD"),
    "endpoint": os.environ.get("SMTP_ENDPOINT"),
    "port": int(os.environ.get("SMTP_PORT", 465)),
    "from_address": os.environ.get("SMTP_FROM_ADDRESS"),
}
"""Settings for connecting to the SMTP email server."""
