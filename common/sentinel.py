from enum import Enum


class Sentinel(Enum):
    """Sentinel object (as Enum for type checking unless PEP-661 is ever approved)."""

    _ = object()


SENTINEL = Sentinel._
