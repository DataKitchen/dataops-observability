from __future__ import annotations

from typing import Any, TypeVar, cast
from collections.abc import Callable

PropertyType = TypeVar("PropertyType")


class cached_property[PropertyType]:
    """
    A `property` decorator that caches the value on the instance.

    The standard library currently has an implementation of a property decorator: ``functools.cached_property`` however
    this version implements locking and it does so in a way that harms performance. The lock is held across EVERY
    instance instead of only the instance the property is attached to. This causes performance issues. For more
    information on this see: https://discuss.python.org/t/finding-a-path-forward-for-functools-cached-property/23757

    Some potential alternatives to ``functools.cached_property``:

    - Boltons: ``cacheutils.cachedproperty``
    - The ``cached_property`` package available in the Python Package Registry
    - Django: Bundles an implementation which could be swiped and vendored

    Neither ``mypy`` nor ``pyright`` can infer type annotations for any of these options. Mypy and Pyright include
    special handling for the functools.

    This implementation verifiably performs *at least* as well as all of the previously mentioned options (and is
    faster than the builtin version). It also has the added benefit of honoring type hints for decorated functions. It
    was inspired by the Django implementation.

    Usage::

        >>> from common.decorators import cached_property
        >>> class Coordinates:
        ...     def __init__(self, x: int, y: int, z: int) -> None:
        ...         self.x = x
        ...         self.y = y
        ...         self.z = z
        ...     @cached_property
        ...     def middle(self) -> int:
        ...         avg = (self.x * self.y * self.z) / 3
        ...         return int(avg)
        ...
        >>> v = Values(2, 3, 4)
        >>> v.middle
        8

    """

    _name: str | None = None

    def __init__(self, f: Callable[[Any], PropertyType]) -> None:
        self.func = f
        self.__doc__ = f.__doc__  # Keep the original docstring

    def __set_name__(self, owner: type[object], name: str) -> None:
        if self._name is None:
            self._name = name
        elif name != self._name:
            raise TypeError(f"Cannot assign the same instance to two names ({self._name} and {name}).")

    def __get__(self, inst: object, cls: Any | None = None) -> PropertyType:
        """
        Retrieve the value from instance, stashing the result in inst.__dict__

        By stashing the value on ``inst.__dict__``, additional attemps to access the property by name will return the
        cached value without invoking the decorator. It also ensures that `delattr` works as expected.
        """
        if inst is None:
            return cast(PropertyType, self)
        if (name := self._name) is None:
            raise TypeError("`cached_property` decorator used without calling __set_name__()")
        res = inst.__dict__[name] = self.func(inst)
        return res
