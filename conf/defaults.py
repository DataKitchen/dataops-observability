RULE_REFRESH_SECONDS: int = 30
"""Number of seconds to cache rules in rules engine"""


MIGRATIONS_SRC_PATH = "/dk/lib/migrations"
"""Yoyo migrations source folder."""

AGENT_STATUS_CHECK_DEFAULT_INTERVAL_SECONDS: int = 300
"""Default polling internal for Agent status changes."""

AGENT_STATUS_CHECK_UNHEALTHY_FACTOR: float = 2
"""Multiplier factor to consider an Agent unhealthy, based on the checking interval."""

AGENT_STATUS_CHECK_OFFLINE_FACTOR: float = 4
"""Multiplier factor to consider an Agent offline, based on the checking interval."""
