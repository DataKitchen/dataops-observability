__all__ = ["not_empty"]

from functools import partial
from collections.abc import Callable

from marshmallow import validate

not_empty: Callable = partial(validate.Length, min=1)
"""
A lot of times, we just want to validate that some message exists and is non-empty. Field classes such as
 Str class do not check the booleanness of a string, nor its length without a validator like this. As for why
It's a partial like this; I thought it'd be more readable considering it's used so many places.
"""
