EXTENDED_ALPHANUMERIC_REGEX = r"^(?!_)[\w ]*(?<!_)$"
"""Alphanumeric string including space and underscore. It cannot start/end with underscore"""

MIN_AGENT_CHECK_INTERVAL_SECONDS: int = 60
"""The minimum interval to check for an agent status."""

MAX_AGENT_CHECK_INTERVAL_SECONDS: int = 24 * 60 * 60
"""The maximum interval to check for an agent status."""
