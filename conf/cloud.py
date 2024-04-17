import json
import os

from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectingPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


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


KAFKA_CONNECTION_PARAMS: dict[str, object] = json.loads(os.environ.get("KAFKA_CONNECTION_PARAMS", "{}"))
"""Settings to connect to Kafka."""
