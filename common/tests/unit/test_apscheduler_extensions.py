from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from apscheduler.triggers.cron import CronTrigger

from common.apscheduler_extensions import (
    DelayedTrigger,
    fix_weekdays,
    get_crontab_trigger_times,
    validate_cron_expression,
)


@pytest.mark.unit
def test_delayed_trigger_negative():
    cron_trigger = CronTrigger.from_crontab("*/2 * * * *", timezone=timezone.utc)
    delay = timedelta(hours=-1)
    with pytest.raises(ValueError, match="positive"):
        DelayedTrigger(cron_trigger, delay)


@pytest.mark.unit
@pytest.mark.parametrize(
    "expression",
    (
        "0 0 1 1 0",
        "  59 23 31 12 6",
        "* * * * *  ",
        "*/4 */2 *   * fri",
        "1-59  1-23  1-31  1-12  0-6",
        "* * * may wed,fri",
        "* * */2 FEB MON-FRI",
    ),
    ids=("min values", "max values", "wildcard values", "intervals", "ranges", "names", "names uppercase"),
)
def test_validate_cron_expression_valid(expression):
    errors = validate_cron_expression(expression)
    assert len(errors) == 0, errors


@pytest.mark.unit
@pytest.mark.parametrize(
    "expression,expected_errors",
    (
        ("* *", 1),
        ("* * * * * *", 1),
        ("60 24 32 13 8", 5),
        ("& $ @ ! .", 5),
        ("* * * invalid invalid", 2),
    ),
    ids=(
        "missing fields",
        "extra field",
        "invalid ranges",
        "invalid field expressions",
        "invalid month and day of week values",
    ),
)
def test_validate_cron_expression_invalid(expression, expected_errors):
    errors = validate_cron_expression(expression)
    assert len(errors) == expected_errors, errors


@pytest.mark.unit
def test_validate_cron_expression_internal_error():
    with patch("apscheduler.triggers.cron.DayOfMonthField.__init__") as field_mock:
        field_mock.side_effect = Exception
        errors = validate_cron_expression("* * * * *")
    assert len(errors) == 1
    assert "could not" in errors[0]


@pytest.mark.unit
@pytest.mark.parametrize(
    "weekday_expression, expected",
    (
        ("*", "SUN,MON,TUE,WED,THU,FRI,SAT"),
        ("*/10", "SUN"),
        ("*/3", "SUN,WED,SAT"),
        ("0-6", "SUN,MON,TUE,WED,THU,FRI,SAT"),
        ("1-7", "MON,TUE,WED,THU,FRI,SAT,SUN"),
        ("1-7/2", "MON,WED,FRI,SUN"),
        ("0", "SUN"),
        ("7", "SUN"),
        ("2", "TUE"),
        ("tue", "TUE"),
        ("WED", "WED"),
        ("3,4", "WED,THU"),
        ("3-6", "WED,THU,FRI,SAT"),
        ("5-7", "FRI,SAT,SUN"),
        # 'Overflowing' ranges
        ("SUN-TUE", "SUN,MON,TUE"),
        ("0-2", "SUN,MON,TUE"),
    ),
)
def test_fix_weekdays(weekday_expression, expected):
    resulting_expression = fix_weekdays(f"* * * * {weekday_expression}").split()[4]
    assert resulting_expression == expected


@pytest.mark.unit
def test_get_crontab_trigger_times_finite_range():
    start = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2000, 1, 10, 0, 0, 0, tzinfo=timezone.utc)
    for i, time in enumerate(get_crontab_trigger_times("0 10 * * *", ZoneInfo("UTC"), start, end)):
        assert time == start + timedelta(days=i, hours=10)
    assert i == 8


@pytest.mark.unit
def test_get_crontab_trigger_times_infinite_range():
    start = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    gen = get_crontab_trigger_times("0 10 * * *", ZoneInfo("UTC"), start)
    for i in range(5000):
        assert next(gen) == start + timedelta(days=i, hours=10)


@pytest.mark.unit
@pytest.mark.parametrize(
    "start,end",
    (
        (datetime(2000, 1, 1, 0, 0, 0), None),
        (datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2000, 1, 2, 0, 0, 0)),
    ),
)
def test_get_crontab_trigger_times_invalid_range(start, end):
    with pytest.raises(ValueError):
        next(get_crontab_trigger_times("0 10 * * *", ZoneInfo("UTC"), start, end))
