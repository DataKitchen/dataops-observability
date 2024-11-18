__all__ = ["DelayedTrigger", "validate_cron_expression", "get_crontab_trigger_times"]

import logging
import re
from datetime import datetime, timedelta
from typing import Optional
from collections.abc import Generator
from zoneinfo import ZoneInfo

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import BaseField, CronTrigger, DayOfMonthField, DayOfWeekField, MonthField

LOG = logging.getLogger(__name__)


CRON_EXPRESSION_FIELDS: tuple[tuple[str, type], ...] = (
    ("minute", BaseField),
    ("hour", BaseField),
    ("day", DayOfMonthField),
    ("month", MonthField),
    ("day_of_week", DayOfWeekField),
)


class DelayedTrigger(BaseTrigger):
    """
    Creates a trigger that applies a `timedelta` delay to a given trigger.

    It's especially useful to be used with the CronTrigger, removing the need to manually update the cron parameters
    to match, but can be used with any `BaseTrigger` sub-class.
    """

    def __init__(self, trigger: BaseTrigger, delay: timedelta):
        if delay.total_seconds() < 0:
            raise ValueError("Delay must be a positive `timedelta`")
        self.trigger = trigger
        self.delay = delay

    def get_next_fire_time(self, previous_fire_time: Optional[datetime], now: datetime) -> Optional[datetime]:
        if previous_fire_time:
            previous_fire_time -= self.delay
        next_fire_time: Optional[datetime] = self.trigger.get_next_fire_time(previous_fire_time, now)
        return next_fire_time + self.delay if next_fire_time else None

    def __str__(self) -> str:
        return f"delayed[{self.trigger}, delay={self.delay}]"


def validate_cron_expression(expression: str) -> list[str]:
    """
    Validates the given cron-like expression against what `CronTrigger.from_expression()` expects.

    Returns a list of strings containing the errors found. The expression should be considered valid when the returned
    list is empty.
    """
    values = fix_weekdays(expression).split()
    errors: list[str] = list()
    if len(values) != 5:
        errors.append(f"Got {len(values)} fields. Expected 5.")

    for (field_name, field_class), value in zip(CRON_EXPRESSION_FIELDS, values, strict=True):
        try:
            field_class(field_name, value)
        except ValueError:
            errors.append(f"'{value}' is not a valid value for the {field_name.replace('_', ' ')} field.")
        except Exception:
            LOG.exception("Exception happened when validating '%s' against the '%s' cron field", value, field_name)
            errors.append(f"'{value}' could not be validated for the {field_name.replace('_', ' ')} field.")

    return errors


def fix_weekdays(expression: str) -> str:
    """
    This function works around https://github.com/agronholm/apscheduler/issues/495 by converting any weekday range
    into a list, considering 0 to be Sunday (instead of Monday) and additionally supporting 7 as Sunday.

    Since it has to run before any validations or processing, it fails silently when it's not possible to fix the
    weekdays.
    """
    try:
        *expr, weekday_expr = expression.split()
        if len(expr) != 4:
            return expression

        weekday_names = ("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
        # We convert the full range into a numeric range to obtain a consistent index for ranges with step > 1
        weekday_expr = weekday_expr.replace("*", "0-6")
        # Given that Sunday is still the first weekday in the underlying implementation, ranges like SUN-TUE would not
        # work, so we convert named weekdays to numbers
        weekday_expr = re.sub(
            f"({'|'.join(weekday_names[:-1])})",
            lambda m: str(weekday_names.index(m.group(1).upper())),
            weekday_expr,
            flags=re.IGNORECASE,
        )
        # Converting any ranges to a list. This is a step on its own to allow existing lists to be considered. The step
        # is also considered. Example: 1,3-6/2 will be converted into 1,3,5
        weekday_expr = re.sub(
            r"(\d+)-(\d+)(/?\d*)",
            lambda m: ",".join(map(str, range(int(m.group(1)), int(m.group(2)) + 1, int(m.group(3)[1:] or 1)))),
            weekday_expr,
        )
        # Fixing the staring index by replacing the numbers with the weekday name
        weekday_expr = re.sub(r"(\d+)", lambda m: weekday_names[int(m.group(1))], weekday_expr)
    except (IndexError, ValueError):
        return expression
    return " ".join((*expr, weekday_expr))


def get_crontab_trigger_times(
    crontab: str, timezone: ZoneInfo, start_range: datetime, end_range: Optional[datetime] = None
) -> Generator[datetime, None, None]:
    """
    Generate the crontab trigger times for the given time range.

    The range must start somewhere but may be endless if desired.
    """
    if not start_range.tzinfo or (end_range and not end_range.tzinfo):
        raise ValueError("The time range must be timezone aware")

    cron_trigger = CronTrigger.from_crontab(fix_weekdays(crontab), timezone)
    trigger_time = start_range
    while (trigger_time := cron_trigger.get_next_fire_time(trigger_time, trigger_time)) is not None and (
        end_range is None or trigger_time < end_range
    ):
        yield trigger_time
