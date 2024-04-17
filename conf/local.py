from pathlib import Path

from peewee import SqliteDatabase

PROJECT_ROOT = Path(__file__).parent.parent

DATABASE: dict[str, object] = {
    "name": PROJECT_ROOT.joinpath("test.db"),
    "engine": SqliteDatabase,
    "pragmas": {
        "journal_mode": "wal",
        "cache_size": -1,  # 10000 pages, or ~40MB
        "foreign_keys": 1,  # Enforce foreign-key constraints
        "ignore_check_constraints": 0,  # enforce CHECK constraints
        "case_sensitive_like": True,  # Case sensitive queries
    },
}
"""Settings for a local sqlite database running locally."""
