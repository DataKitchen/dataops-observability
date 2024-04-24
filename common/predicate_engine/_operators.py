from __future__ import annotations

__all__ = ("get_operator", "get_operators", "split_operators", "OPERAND_MAP", "QueryOperator", "OperandLiteral")

import logging
import operator
import re
from functools import cache
from typing import TYPE_CHECKING, Any, Callable, Literal, cast

if TYPE_CHECKING:
    from .query import R

LOG = logging.getLogger(__name__)
SENTINEL_NONE = object()  # Fake None singleton (to avoid confusion with None comparisons)

QueryOperator = Callable[[Any, Any], bool]
"""The type signature for an operator callable."""


# Operator functions
def _startswith(x: Any, y: Any) -> bool:
    return bool(x.startswith(y))


def _istartswith(x: Any, y: Any) -> bool:
    return bool(x.lower().startswith(y.lower()))


def _endswith(x: Any, y: Any) -> bool:
    return bool(x.endswith(y))


def _iendswith(x: Any, y: Any) -> bool:
    return bool(x.lower().endswith(y.lower()))


def _range(x: Any, y: Any) -> bool:
    return bool(y[0] <= x <= y[1])


def _isnull(x: Any, y: Any) -> bool:
    return (not x) ^ (not y)


def _regex(x: Any, y: Any) -> bool:
    return bool(re.search(y, x))


def _iregex(x: Any, y: Any) -> bool:
    return bool(re.search(y, x, re.IGNORECASE))


def _iexact(x: Any, y: Any) -> bool:
    return bool(x.lower() == y.lower())


def _icontains(x: Any, y: Any) -> bool:
    return y.lower() in x.lower()


def _in(x: Any, y: Any) -> bool:
    return operator.contains(y, x)


def _r(x: Any, y: R) -> bool:
    return y.matches(x)


OperandLiteral = Literal[
    "contains",
    "endswith",
    "exact",
    "gt",
    "gte",
    "icontains",
    "iendswith",
    "iexact",
    "in",
    "iregex",
    "isnull",
    "istartswith",
    "lt",
    "lte",
    "r",
    "range",
    "regex",
    "startswith",
]
"""All valid operator name literals."""


OPERAND_MAP: dict[str, QueryOperator] = {
    "contains": operator.contains,
    "endswith": _endswith,
    "exact": operator.eq,
    "gt": operator.gt,
    "gte": operator.ge,
    "icontains": _icontains,
    "iendswith": _iendswith,
    "iexact": _iexact,
    "in": _in,
    "iregex": _iregex,
    "isnull": _isnull,
    "istartswith": _istartswith,
    "lt": operator.lt,
    "lte": operator.le,
    "r": _r,
    "range": _range,
    "regex": _regex,
    "startswith": _startswith,
}
"""A map of operators to their comparsion function."""


def split_operators(op_string: str) -> tuple[str, OperandLiteral]:
    """
    Return the attribute & operator names from a string of the form attrname__operator.

    i.e. Given a string of the form ``attr_name__op`` return the attr_name and the operation as a tuple pair. If no
    operator is given, the value is presumed to be an attribute name only and the default operator ``exact`` is used.
    """
    parts: list[str] = [x for x in op_string.rsplit("__", maxsplit=1) if x]
    if not parts:
        raise ValueError(f"Invalid operator string: `{op_string}`")
    elif len(parts) != 2:
        raise ValueError(
            f"Operator string `{op_string}` is malformed, possibly missing an operator. "
            f"Maybe you meant `{parts[0]}_exact`?"
        )
    else:
        attr_name = parts[0]
        op = parts[1]
        if op not in OPERAND_MAP:
            raise ValueError(
                f"Operator string `{op_string}` is malformed, `{op}` is not a valid operator. Perhaps it is misspelled"
                f" or perhaps you meant `{parts[0]}_exact`?"
            )
        else:
            _op = cast(OperandLiteral, op)
            return (attr_name, _op)


@cache
def get_operator(op_name: OperandLiteral) -> QueryOperator:
    """Lookup an operator from it's name."""
    try:
        return OPERAND_MAP[op_name]
    except KeyError as e:
        raise ValueError(f"Unknown operator `{op_name}`") from e


@cache
def get_operators(op_string: str) -> tuple[str, QueryOperator]:
    """
    Return the attribute name & operator callable from an operator string of the form attrname__operator.

    i.e. Given a string of the form ``attr_name__op`` return the attr_name and the operation as a tuple pair. If no
    operator is given, the value is presumed to be an attribute name only and the default operator ``exact`` is used.
    """
    attr_name, op_name = split_operators(op_string)
    op_func = get_operator(op_name)
    return (attr_name, op_func)
