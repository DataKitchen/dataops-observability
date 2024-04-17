from peewee import SqliteDatabase

DATABASE = {
    "name": "file:cachedb?mode=memory&cache=shared",
    "engine": SqliteDatabase,
    "pragmas": {},
}
"""Configures an in-memory database with a shared cache for testing."""

API_PREFIX: str = "events"

TESTING: bool = True
"""Enable flask TESTING mode. This is needed to get around the default-key security check."""
