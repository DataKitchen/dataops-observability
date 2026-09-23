from __future__ import annotations

__all__ = ["ConnectorType", "rule_to_predicate", "get_rule_fields"]

import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from copy import copy, deepcopy
from datetime import datetime, UTC
from enum import Enum
from functools import partial, reduce
from typing import Any, Final, Union
from collections.abc import Callable, Iterable

from ._operators import QueryOperator, get_operator, get_operators, split_operators

LOG = logging.getLogger(__name__)
SENTINEL_NONE = object()  # Fake None singleton (to avoid confusion with None comparisons)

NULL_OPERATOR: Final[QueryOperator] = get_operator("isnull")
"""The is_null predicate function."""


def _ensure_utc(dt: datetime) -> datetime:
    """
    Ensures that a value is TZ aware and in UTC time.

    If a value is naive, assume it to be UTC and add UTC tzinfo, if there is already tzinfo, convert it to UTC.

        >>> naive_dt = datetime(2006, 11, 6, 10, 10, 10)
        >>> tzaware = naive_dt_to_utc(naive_dt)
        >>> tzaware.isoformat()
        '2006-11-06T10:10:10+00:00'
    """
    if (tzinfo := dt.tzinfo) is None:
        return dt.replace(tzinfo=UTC)
    if tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def getattr_recursive(lookup_obj: Any, attr_name: str, *args: Any) -> Any:
    """Recursively follow attribute spanning notation up the chain. 'foo__bar__baz'"""

    def _getattr(obj: Any, attr: str) -> Any:
        if isinstance(obj, Mapping) and attr in obj:
            try:
                ret_val = obj.get(attr, SENTINEL_NONE)
            except Exception:
                return getattr(obj, attr, *args)  # Fall back to normal getattr
            if ret_val is SENTINEL_NONE:
                return getattr(obj, attr, *args)  # Fall back to normal getattr
            else:
                return ret_val
        return getattr(obj, attr, *args)

    return reduce(_getattr, [lookup_obj] + attr_name.split("__"))


class ConnectorType(Enum):
    OR = "OR"
    AND = "AND"


class _Encapsulate(ABC):
    """
    Encapsulate a value to annotate a value during a predicate operation.

    This class cannot be used directly, instead it should be subclassed for each type of annotation and a ``matches``
    method must be written.
    """

    __slots__ = ("wrapped_value", "attr_name", "transform_funcs")

    def __init__(
        self,
        value: object,
        *,
        attr_name: str | None = None,
        transform_funcs: Iterable[Callable[..., Iterable]] | None = None,
    ) -> None:
        self.wrapped_value = value
        self.attr_name = attr_name
        self.transform_funcs = transform_funcs

    def _prepare_values(self, instance_value: Iterable) -> Iterable:
        values = instance_value
        for fn in self.transform_funcs or []:
            values = fn(values)
        if (attr_name := self.attr_name) is not None:
            an = attr_name  # Workaround: https://github.com/python/mypy/issues/4297
            values = map(lambda item: getattr_recursive(item, an, SENTINEL_NONE), values)
        return values

    @abstractmethod
    def matches(self, *, op_func: Callable[..., bool], instance_value: Iterable) -> bool:
        """Define a match method."""
        ...

    def __str__(self) -> str:
        return f"<ALL: {self.wrapped_value}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _Encapsulate):
            return False
        else:
            if other.wrapped_value == self.wrapped_value and other.__class__ is self.__class__:
                return True
            else:
                return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __deepcopy__(self, memo: dict) -> _Encapsulate:
        """Perform a deep copy of this ``_Encapsulate`` object instance."""
        obj = self.__class__(deepcopy(self.wrapped_value))
        return obj

    def __copy__(self) -> _Encapsulate:
        """Perform a shallow copy of this ``_Encapsulate`` object instance."""
        obj = self.__class__(copy(self.wrapped_value))
        return obj


class ANY(_Encapsulate):
    """
    Encapsulate a value to indicate an ANY predicate operation on an iterable.

    Indicates that the operator should be applied to all values of the wrapped iterable value rather than on the
    object as a whole. The match should be successful if **any** of the values in the array match the given operator.
    """

    def __str__(self) -> str:
        return f"<ANY: {self.wrapped_value}>"

    def matches(self, *, op_func: Callable[..., bool], instance_value: Iterable) -> bool:
        """Attempt the match."""
        val = self.wrapped_value
        for item in self._prepare_values(instance_value):
            if op_func(item, val):
                return True
        return False


class ALL(_Encapsulate):
    """
    Encapsulate a value to indicate an ALL predicate operation on an iterable.

    Indicates that the operator should be applied to all values of the wrapped iterable value rather than on the
    object as a whole. The match should be successful if **all** of the values in the array match the given operator.
    """

    def matches(self, *, op_func: Callable[..., bool], instance_value: Iterable) -> bool:
        """Attempt the match."""
        val = self.wrapped_value
        for item in self._prepare_values(instance_value):
            if not op_func(item, val):
                return False
        return True


class EXACT_N(_Encapsulate):
    """
    Encapsulate a value to indicate an EXACT Number predicate operation on an iterable.

    The match should be successful if the first N values match the given operator, and if it exists, N+1 should NOT
    match.
    """

    __slots__ = ("count",)

    def __init__(
        self,
        value: object,
        *,
        n: int,
        attr_name: str | None = None,
        transform_funcs: Iterable[Callable[..., Iterable]] | None = None,
    ) -> None:
        self.count = n
        super().__init__(value, attr_name=attr_name, transform_funcs=transform_funcs)

    def __str__(self) -> str:
        return f"<EXACT_N: {self.wrapped_value}, N: {self.count}>"

    def matches(self, *, op_func: Callable[..., bool], instance_value: Iterable) -> bool:
        val = self.wrapped_value
        i = 0
        for i, item in enumerate(self._prepare_values(instance_value), start=1):
            if i > self.count:
                if op_func(item, val):
                    return False
                break
            if not op_func(item, val):
                return False
        return i >= self.count


class ATLEAST(_Encapsulate):
    """
    Encapsulate a value to indicate an ATLEAST predicate operation on an iterable.

    The match should be successful if ATLEAST the N first values are matching.
    """

    __slots__ = ("count",)

    def __str__(self) -> str:
        return f"<ATLEAST: {self.wrapped_value}, N: {self.count}>"

    def __init__(
        self,
        value: object,
        *,
        n: int,
        attr_name: str | None = None,
        transform_funcs: Iterable[Callable[..., Iterable]] | None = None,
    ) -> None:
        self.count = n
        super().__init__(value, attr_name=attr_name, transform_funcs=transform_funcs)

    def matches(self, *, op_func: Callable[..., bool], instance_value: Iterable) -> bool:
        val = self.wrapped_value
        i = 0
        for i, item in enumerate(self._prepare_values(instance_value), start=1):
            if i > self.count:
                break
            if not op_func(item, val):
                return False
        return i >= self.count


def rule_to_predicate(rtree: Union[R, tuple[str, object]]) -> Callable[[object], bool]:
    """Given a rules object (R), return a predicate function which determines whether an object matches the rule."""
    if isinstance(rtree, R):
        rule_obj: R = rtree
        # Resolve the rules object into separate predicates and combine according to their connectors
        if rule_obj.conn_type is ConnectorType.AND:
            predicate_wrapper = all
        elif rule_obj.conn_type is ConnectorType.OR:
            predicate_wrapper = any
        # Logical XOR to negate the result if needed
        return lambda instance: rule_obj.negated ^ predicate_wrapper(
            rule_to_predicate(child)(instance) for child in rule_obj.children
        )

    else:
        child_obj: tuple[str, object] = rtree

        def op_compare(instance: Any, *, compare_value: Any, attr_name: str, op_func: QueryOperator) -> bool:
            inst_value = getattr_recursive(instance, attr_name, SENTINEL_NONE)
            if inst_value is SENTINEL_NONE:
                # For __isnull=True, a missing attribute should be a successful match (it's VERY null)
                if op_func is NULL_OPERATOR and compare_value is True:
                    return True
                # Fail all other comparisons
                return False

            if isinstance(compare_value, _Encapsulate):
                try:
                    return compare_value.matches(op_func=op_func, instance_value=inst_value)
                except TypeError:
                    # See TypeError in the next try/except block
                    return False
                except AttributeError:
                    # See AttributeError in the next try/except block
                    return False

            try:
                return bool(op_func(inst_value, compare_value))
            except TypeError:
                # If instance.attr_name is None, not all operators can handle that comparison and instead raise a
                # TypeError. For those cases, we simply return False. If we happen to be attempting to compare two
                # datetime objects, one of which is naive, AND if the operator is one which directly compares the two
                # values, then coerce them UTC and retry the comparison.
                if isinstance(inst_value, datetime) and isinstance(compare_value, datetime):
                    _inst_utc = _ensure_utc(inst_value)
                    _comp_utc = _ensure_utc(compare_value)
                    try:
                        if op_func(_inst_utc, _comp_utc):
                            return True
                        else:
                            return False
                    except Exception:
                        LOG.warning("Error comparing %s to %s", _inst_utc, _comp_utc, exc_info=True)
                        return False
                else:
                    return False
            except AttributeError:
                # The comparision depended on attributes that one of the values to compare does not have. i.e. a None
                # will not have a .lower() function and so case insensitive matches cannot be performed. Since such
                # comparisons make no sense anyway, this is a failed match as well.
                return False

        # A left/right side comparison setup - left side is the attribute name and optionally, an operator string
        # while the right side is the value to compare against
        op_key: str = child_obj[0]
        compare_value: object = child_obj[1]

        # Create a predicate function for a leaf node
        attr_name, op_func = get_operators(op_key)
        func = partial(op_compare, compare_value=compare_value, attr_name=attr_name, op_func=op_func)
        func.__doc__ = f"Comparison callable for rule: {rtree}"

        return func


class R:
    """
    Encapsulate rules as objects that can then be combined using & and |

    This is an implementation of a tree node for making expressions which can be used to construct rules of arbitrary
    complexity. It is loosely inspired by the Q-object implementation in Django but is object agnostic and not meant for
    an ORM.
    """

    __slots__ = ("children", "conn_type", "negated")

    AND = ConnectorType.AND
    OR = ConnectorType.OR
    default = ConnectorType.AND

    def __init__(self, **kwargs: object) -> None:
        # Make kwargs into a list of tuple key/value pairs so it can be appended to
        self.children: list[Union[R, tuple[str, object]]] = list(kwargs.items())
        self.conn_type = self.AND  # Default to AND on new object construction.
        self.negated = False

    @classmethod
    def _new_instance(
        cls, children: list | None = None, conn_type: ConnectorType = ConnectorType.AND, negated: bool = False
    ) -> R:
        """
        Creates a new instance of this class.

        The function signature of __init__ doesn't accept all of these arguments (on purpose). This allows the
        construction of a new node with the given attributes. Used by add and negate functions.
        """
        rule = R()
        rule.children = children or []
        rule.conn_type = conn_type
        rule.negated = negated
        return rule

    def __copy__(self) -> R:
        return self._new_instance(children=self.children[:], conn_type=self.conn_type, negated=self.negated)

    def _combine(self, other: R, conn_type: ConnectorType) -> R:
        """Combine this object with another object and return a new combined instance."""
        if not isinstance(other, R):
            raise TypeError(other)
        if self and not other:
            return copy(self)
        if not self and not other and other.conn_type == self.conn_type:
            return copy(self)
        obj = self._new_instance(children=[], conn_type=conn_type, negated=False)
        obj.add(self, conn_type=conn_type)
        obj.add(other, conn_type=conn_type)
        return obj

    def __or__(self, other: R) -> R:
        return self._combine(other, self.OR)

    def __and__(self, other: R) -> R:
        return self._combine(other, self.AND)

    def __invert__(self) -> R:
        """Create and return an inverted version of this Rule."""
        # Create a new R object instance
        obj = R()

        # Set connector type to AND (top level) and default, new object will have one child
        obj.add(self, conn_type=self.AND)

        # Create a new instance of the current rule with the negated attribute flipped. Make the negated instance a
        # child of the new R object.
        obj.children = [self._new_instance(self.children, self.conn_type, not self.negated)]
        return obj

    def __str__(self) -> str:
        if self.negated:
            return f"(NOT ({self.conn_type.value}: {', '.join([str(c) for c in self.children])}))"
        return f"({self.conn_type.value}: {', '.join([str(c) for c in self.children])})"

    def __len__(self) -> int:
        """A rule nodes size is it's number of children."""
        return len(self.children)

    def __bool__(self) -> bool:
        return bool(self.children)

    def __contains__(self, other: Union[R, object]) -> bool:
        """True only if `other` is a direct child of this instance (does not recurse)."""
        if other in self.children:
            return True
        else:
            return False

    def add(self, node: R, *, conn_type: ConnectorType) -> None:
        """Add a new node to the rules tree."""
        if len(self.children) < 2:
            self.conn_type = conn_type
        if self.conn_type is conn_type:
            if isinstance(node, R) and (node.conn_type is conn_type or len(node) == 1):
                self.children.extend(node.children)
            else:
                self.children.append(node)
        else:
            obj = self._new_instance(self.children, self.conn_type, self.negated)
            self.conn_type = conn_type
            self.children = [obj, node]

    def matches(self, instance: object) -> bool:
        """Determine if an instance matches this search tree."""
        match: bool = rule_to_predicate(self)(instance)
        return match


def get_rule_fields(search_object: Union[R, tuple[str, Any]]) -> set[str]:
    """Descend through a R object tree and extract all fieldnames used."""
    fields = set()
    if isinstance(search_object, tuple):
        fieldname, _ = split_operators(search_object[0])
        # The __ notation is not used now, but we may support spanning searches in the future
        fieldname = fieldname.split("__", 1)[-1]
        fields.add(fieldname)
        return fields
    for child_tuple in search_object.children:
        child_fields = get_rule_fields(child_tuple)
        fields.update(child_fields)
    return {x for x in fields}
