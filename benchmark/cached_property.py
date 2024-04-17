from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property as py_cached_property

import pyperf
from boltons.cacheutils import cachedproperty as boltons_cached_property

from common.decorators import cached_property as observability_cached_property

# This is my own modification of a benchmark used by the Django project when it was evaluating the standard library's
# cached_property implementation. See: <https://code.djangoproject.com/ticket/30949#comment:9 for more info.

SLEEP_TIME = 0.01  # Most web requests have some IO, like database access. Simulate with sleeping


class django_cached_property:
    """A copy of the Django implementation copy/pasted so we don't have to have Django as a benchmark dependency."""

    name = None

    @staticmethod
    def func(instance):
        raise TypeError("Cannot use cached_property instance without calling __set_name__() on it.")

    def __init__(self, func, name=None):
        self.real_func = func
        self.__doc__ = getattr(func, "__doc__")

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same cached_property to two different names (%r and %r)." % (self.name, name)
            )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class TestClass:
    @boltons_cached_property
    def boltons_cached(self):
        time.sleep(SLEEP_TIME)
        return "Test"

    @py_cached_property
    def py_cached(self):
        time.sleep(SLEEP_TIME)
        return "Test"

    @django_cached_property
    def django_cached(self):
        time.sleep(SLEEP_TIME)
        return "Test"

    @observability_cached_property
    def observability_cached(self):
        time.sleep(SLEEP_TIME)
        return "Test"


def test_boltons():
    t = TestClass()
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached
    t.boltons_cached


def test_django():
    t = TestClass()
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached
    t.django_cached


def test_python():
    t = TestClass()
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached
    t.py_cached


def test_ql():
    t = TestClass()
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached
    t.observability_cached


def boltons_cache(loops):
    range_it = range(loops)
    t0 = pyperf.perf_counter()

    for loop in range_it:
        with ThreadPoolExecutor() as executor:
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)
            executor.submit(test_boltons)

    return pyperf.perf_counter() - t0


def django_cache(loops):
    range_it = range(loops)
    t0 = pyperf.perf_counter()

    for loop in range_it:
        with ThreadPoolExecutor() as executor:
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)
            executor.submit(test_django)

    return pyperf.perf_counter() - t0


def python_cache(loops):
    range_it = range(loops)
    t0 = pyperf.perf_counter()

    for loop in range_it:
        with ThreadPoolExecutor() as executor:
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)
            executor.submit(test_python)

    return pyperf.perf_counter() - t0


def observability_cache(loops):
    range_it = range(loops)
    t0 = pyperf.perf_counter()

    for loop in range_it:
        with ThreadPoolExecutor() as executor:
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)
            executor.submit(test_ql)

    return pyperf.perf_counter() - t0


runner = pyperf.Runner()
runner.bench_time_func("Standard Library", python_cache)
runner.bench_time_func("Boltons", boltons_cache)
runner.bench_time_func("Django", django_cache)
runner.bench_time_func("Observability Implementation", observability_cache)
