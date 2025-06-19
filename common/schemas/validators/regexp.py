__all__ = ["IsRegexp"]

import re

from marshmallow import ValidationError
from marshmallow.validate import Validator


class IsRegexp(Validator):
    """
    Validates the input string is a regular expression.
    """

    message_invalid = "Invalid regular expression"

    def __init__(self, *, error: str | None = None) -> None:
        self.error: str = error or self.message_invalid

    def __call__(self, value: str) -> str:
        try:
            re.compile(value)
        except Exception as e:
            raise ValidationError(self.error.format(input=value)) from e
        return value
