from datetime import datetime, timezone

import pytest


class EntityClass:
    """Test class for object matching tests"""

    def __init__(self, a: object, b: object, total_things=4) -> None:
        self.a = a
        self.b = b
        self.total_things = total_things
        self.str_value = "fleem"
        self.int_value = 42  # It's always gonna be 42 man
        self.null_value = None
        self.status = "COMPLETED_WITH_WARNINGS"
        self.run_key = "fc392d70-85b6-4f9a-803c-88143a519c3c"

    def __str__(self):
        return f"{self.a} - {self.b}"

    @property
    def averages(self) -> int:
        return 3

    @property
    def null(self) -> None:
        return None

    @property
    def timestamp(self) -> datetime:
        return datetime(1983, 10, 20, 10, 10, 10)

    @property
    def timestamp_dt(self) -> datetime:
        return datetime(1983, 10, 20, 10, 10, 10, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def simple_entity():
    yield EntityClass(3, "test")


@pytest.fixture(scope="session")
def nested_entity():
    inner = EntityClass(3, "test")
    middle = EntityClass(inner, "test")
    outer = EntityClass(middle, "test")
    yield outer
