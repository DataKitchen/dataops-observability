import os

from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectingPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


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
