HASH_ITERATIONS: int = 390_000
"""
Default iterations for hashing a supplied password.

This number is picked somewhat at random. It needs to be significantly large to yield an appropriate work factor
but the exact value doesn't matter.
"""

DEFAULT_EXPIRY_DAYS: int = 365
"""Default length of time an API key is valid; defaults to 1 year (365 days)."""
