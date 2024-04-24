"""
Test type revealations for decorators.

This isn't a *unit* test per-say, but rather a stub file that validates the type inference of the cached_property
decorator in ``common.decorators``. If the inferred hints do not match then mypy will raise an error. It allows us
to verify that the type inference is working as expected.
"""
from typing import Mapping

from typing_extensions import assert_type

from common.decorators import cached_property

class TestKlass:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    @cached_property
    def test_1(self) -> tuple[int, int]:
        return (self.x, self.y)
    @cached_property
    def test_2(self) -> Mapping[str, int]:
        return {"x": self.x, "y": self.y}

assert_type(TestKlass.test_1, tuple[int, int])  # The inferred type for TestKlass.test_1 should be `tuple[int, int]`
assert_type(TestKlass.test_2, Mapping[str, int])  # The inferred type for TestKlass.test_2 should be `Mapping[str, int]`
