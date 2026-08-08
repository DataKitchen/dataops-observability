from datetime import datetime, timezone, UTC
from zoneinfo import ZoneInfo, available_timezones

import pytest

from common.datetime_utils import datetime_formatted, datetime_iso8601, datetime_to_timestamp, timestamp_to_datetime


@pytest.mark.unit
def test_datetime_formatted():
    aware = datetime.strptime("1999-05-12T17:15:56.123456+2000", "%Y-%m-%dT%H:%M:%S.%f%z")
    assert datetime_formatted(aware) == "May 11, 1999 at 09:15 PM (UTC)"
    naive = datetime.strptime("1999-05-12T17:15:56.123456", "%Y-%m-%dT%H:%M:%S.%f")
    assert datetime_formatted(naive) == "May 12, 1999 at 05:15 PM (UTC)"


@pytest.mark.unit
def test_datetime_iso8601():
    aware = datetime.strptime("1999-05-12T17:15:56.123456+2000", "%Y-%m-%dT%H:%M:%S.%f%z")
    assert datetime_iso8601(aware) == "1999-05-11T21:15:56.123456+00:00"
    naive = datetime.strptime("1999-05-12T17:15:56.123456", "%Y-%m-%dT%H:%M:%S.%f")
    assert datetime_iso8601(naive) == "1999-05-12T17:15:56.123456+00:00"


@pytest.mark.unit
@pytest.mark.parametrize(
    "ts, dt",
    (
        (1685701704.039912, datetime(2023, 6, 2, 10, 28, 24, 39912, tzinfo=UTC)),
        (1123905724.000002, datetime(2005, 8, 13, 4, 2, 4, 2, tzinfo=UTC)),
        (435489642.424242, datetime(1983, 10, 20, 9, 20, 42, 424242, tzinfo=UTC)),
        (1162815179.06429, datetime(2006, 11, 6, 12, 12, 59, 64290, tzinfo=UTC)),
    ),
)
def test_timestamp_and_datetime(ts, dt):
    """Test converting to and from timestamps."""
    converted_dt = timestamp_to_datetime(ts)
    assert dt == converted_dt

    converted_ts = datetime_to_timestamp(dt)
    assert ts == converted_ts


@pytest.mark.unit
def test_tzinfo_added():
    """Converting a naive datetime to a timestamp and back adds tzinfo."""
    naive_dt = datetime(2006, 11, 6, 12, 12)
    timestamp = datetime_to_timestamp(naive_dt)

    expected_dt = datetime(2006, 11, 6, 12, 12, tzinfo=UTC)
    actual_dt = timestamp_to_datetime(timestamp)

    assert actual_dt != naive_dt
    assert expected_dt == actual_dt

    # Asserting on tzinfo; the same datetime in different timezones compare as equal
    assert expected_dt.tzinfo == actual_dt.tzinfo


@pytest.mark.unit
def test_tzinfo_coerced_to_utc():
    """Timestamps are returned in UTC."""
    tzinfo = ZoneInfo(available_timezones().pop())

    tz_dt = datetime(2001, 1, 1, 0, 0, 0, tzinfo=tzinfo)
    timestamp = datetime_to_timestamp(tz_dt)

    expected_dt = tz_dt.astimezone(UTC)
    actual_dt = timestamp_to_datetime(timestamp)

    assert expected_dt == actual_dt

    # Asserting on tzinfo; the same datetime in different timezones compare as equal
    assert tz_dt.tzinfo != actual_dt.tzinfo
    assert expected_dt.tzinfo == actual_dt.tzinfo
