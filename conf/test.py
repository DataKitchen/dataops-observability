from peewee import SqliteDatabase

DATABASE: dict[str, object] = {
    "name": "file:cachedb?mode=memory&cache=shared",
    "engine": SqliteDatabase,
    "pragmas": {"foreign_keys": 1},
    "uri": True,
}
"""Configures an in-memory database with a shared cache for testing."""

KAFKA_CONNECTION_PARAMS: dict[str, str] = {}
"""Empty Kafka connect parameters to please unit tests."""

SMTP: dict[str, object] = {
    "username": "",
    "password": "",
    "endpoint": "",
    "port": 25,
    "from_address": "",
}
"""Dummy SMTP parameters to please unit tests."""
