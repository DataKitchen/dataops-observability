__all__ = ["CronExpressionStr"]

from typing import Any
from collections.abc import Mapping

from marshmallow import ValidationError
from marshmallow.fields import Str

from common.apscheduler_extensions import validate_cron_expression


class CronExpressionStr(Str):
    """
    Field that handles a Cron-like expression as a String value.

    It validates against what ApScheduler's CronTrigger expects.
    """

    def _deserialize(self, value: Any, attr: str | None, data: Mapping[str, Any] | None, **kwargs: object) -> Any:
        str_value = super(Str, self)._deserialize(value, attr, data, **kwargs)
        if errors := validate_cron_expression(str_value):
            raise ValidationError(" ".join(errors))
        return str_value
