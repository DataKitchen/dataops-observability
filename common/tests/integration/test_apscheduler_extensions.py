from datetime import datetime, timedelta, timezone
from itertools import count

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.util import astimezone

from common.apscheduler_extensions import DelayedTrigger


def calculate_fire_time_sequence(trigger, n=10):
    prev_fire_time = None
    now = datetime.now(tz=getattr(trigger, "timezone", timezone.utc))
    for _ in range(n):
        next_fire_time = trigger.get_next_fire_time(prev_fire_time, now)
        yield next_fire_time
        prev_fire_time = next_fire_time
        now = next_fire_time


@pytest.mark.integration
@pytest.mark.parametrize(
    "trigger",
    (
        CronTrigger.from_crontab("*/2 * * * *", timezone=timezone.utc),
        CronTrigger.from_crontab("*/4 * * * *", timezone=timezone.utc),
        CronTrigger(
            year="*",
            month="*",
            day="*",
            hour="*",
            minute="*/4",
            timezone=timezone.utc,
            start_date=datetime.now(tz=timezone.utc) + timedelta(days=5),
        ),
        CronTrigger.from_crontab("*/4 * * * *", timezone=astimezone("Asia/Tokyo")),
        IntervalTrigger(minutes=1, timezone=timezone.utc),
        IntervalTrigger(minutes=6, timezone=timezone.utc),
        DateTrigger(timezone=timezone.utc),
    ),
    ids=(
        "cron_smaller_interval",
        "cron_bigger_interval",
        "cron_w_future_start",
        "cron_not_utc",
        "interval_smaller_interval",
        "interval_bigger_interval",
        "date",
    ),
)
def test_delayed_trigger_3_min_delay(trigger):
    delay = timedelta(minutes=3)
    delayed_trigger = DelayedTrigger(trigger, delay)

    for idx, original, delayed in zip(
        count(), calculate_fire_time_sequence(trigger), calculate_fire_time_sequence(delayed_trigger)
    ):
        expected = original + delay if original else None
        assert delayed == expected, f"original={original}, trigger={trigger}, idx={idx}"


@pytest.mark.integration
@pytest.mark.parametrize(
    "delay",
    (
        timedelta(),
        timedelta(days=6),
        timedelta(hours=12),
        timedelta(minutes=5),
        timedelta(seconds=10),
    ),
)
def test_delayed_trigger(delay):
    cron_trigger = CronTrigger.from_crontab("*/2 * * * *", timezone=timezone.utc)
    delayed_trigger = DelayedTrigger(cron_trigger, delay)

    for idx, original, delayed in zip(
        count(), calculate_fire_time_sequence(cron_trigger), calculate_fire_time_sequence(delayed_trigger)
    ):
        expected = original + delay if original else None
        assert delayed == expected, f"original={original}, delay={delay}, idx={idx}"
