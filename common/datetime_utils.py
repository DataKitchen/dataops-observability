__all__ = ["datetime_formatted", "datetime_iso8601", "to_utc_aware"]
from datetime import datetime, timezone


# Although datetimes in Events are tz aware they only contains the raw offset
# after being marshmallow serialized. Since the tz name is desired astimezone
# is used for strftime to return the name.
def to_utc_aware(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def datetime_formatted(dt: datetime) -> str:
    """Format datetime in the same way that the UI formats datetimes"""
    # "%-d" is Linux specific but the other ways of achieving the same seemed worse.
    return to_utc_aware(dt).strftime("%B %-d, %Y at %I:%M %p (%Z)")


def datetime_iso8601(dt: datetime) -> str:
    return to_utc_aware(dt).isoformat()


def datetime_to_timestamp(dt: datetime) -> float:
    """Convert a datetime to a timestamp."""
    tzaware_dt = to_utc_aware(dt)
    timestamp = tzaware_dt.timestamp()
    return timestamp


def timestamp_to_datetime(timestamp: float) -> datetime:
    """Convert a timestamp to a datetime object in UTC time."""
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt
