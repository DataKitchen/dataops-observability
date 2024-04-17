import pytest

from common.decorators import cached_property


class ExampleObject:
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z

    @cached_property
    def total(self) -> int:
        "Test `total` docstring."
        return self.x + self.y + self.z

    @cached_property
    def __product__(self) -> int:
        "Test `__product__` docstring."
        return self.x * self.y * self.z

    def random_value(self) -> str:
        "Test `random_value` docstring."
        return f"Random: {6 + self.__product__ + self.total}"

    random = cached_property(random_value)

    @cached_property
    def __dunder(self) -> int:
        return abs((self.x + self.y) - self.z)


@pytest.mark.unit
def test_cached_property_docstrings():
    """The cached_property decorator preserves the docstrings of the wrapped function."""
    assert "Test `total` docstring." == getattr(ExampleObject, "total").__doc__
    assert "Test `__product__` docstring." == getattr(ExampleObject, "__product__").__doc__
    assert "Test `random_value` docstring." == getattr(ExampleObject, "random_value").__doc__
    assert "Test `random_value` docstring." == getattr(ExampleObject, "random").__doc__

    class ExampleObjectSubClass(ExampleObject):
        pass

    # Do the same tests but for subclasses
    assert "Test `total` docstring." == getattr(ExampleObjectSubClass, "total").__doc__
    assert "Test `__product__` docstring." == getattr(ExampleObjectSubClass, "__product__").__doc__
    assert "Test `random_value` docstring." == getattr(ExampleObjectSubClass, "random_value").__doc__
    assert "Test `random_value` docstring." == getattr(ExampleObjectSubClass, "random").__doc__


@pytest.mark.unit
def test_cached_property_caches_values():
    """Values are cached in the instances __dict__."""

    instance = ExampleObject(1, 5, 34)

    # Value not (yet) in __dict__
    assert "total" not in instance.__dict__
    assert "__product__" not in instance.__dict__
    assert "random" not in instance.__dict__

    # Correct values are returned
    assert 40 == instance.total
    assert 170 == instance.__product__
    assert "Random: 216" == instance.random

    # After having been accessed, values are now cached on the instance __dict__
    assert "total" in instance.__dict__
    assert "__product__" in instance.__dict__
    assert "random" in instance.__dict__


@pytest.mark.unit
def test_cached_property_no_shared_state():
    """State is not shared between different instances."""
    instance_1 = ExampleObject(1, 5, 4)
    instance_2 = ExampleObject(3, 7, 8)

    assert instance_1.total != instance_2.total


@pytest.mark.unit
def test_cached_property_no_shared_state_subclasses():
    """State is not shared between different subclassed instances."""

    class ExampleObjectSubClass(ExampleObject):
        pass

    instance_1 = ExampleObject(1, 5, 0)
    instance_2 = ExampleObjectSubClass(3, 7, 1)

    assert instance_1.total != instance_2.total


@pytest.mark.unit
def test_cached_property_requires_set_name():
    """The cached_property_decorator requires __set_name__ be called."""
    # Create an instance that is not bound to a class yet
    prop = cached_property(lambda self: None)

    class FooKlass:
        pass

    # Add the cached_property instance to the class
    FooKlass.prop = prop
    expected_msg = "`cached_property` decorator used without calling __set_name__()"

    # At this point, attempting to access the decorator should raise an exception.
    with pytest.raises(TypeError, match=expected_msg):
        FooKlass().prop

    # The same is true if we try to access it on an instance
    instance = FooKlass()
    with pytest.raises(TypeError, match=expected_msg):
        instance.prop


@pytest.mark.unit
def test_original_function_not_modified():
    """Calling the decorator does not turn the original function into a property."""
    assert isinstance(ExampleObject.total, cached_property) is True
    assert isinstance(ExampleObject.__product__, cached_property) is True
    assert isinstance(ExampleObject.random, cached_property) is True

    assert isinstance(ExampleObject.random_value, cached_property) is False
    assert callable(ExampleObject.random_value) is True
    assert callable(ExampleObject.random) is False


@pytest.mark.unit
def test_class_mangled_auto_name():
    """The cached_property decorator still behaves like a decorator on mangled method names."""
    instance = ExampleObject(1, 5, 2)
    assert 4 == instance._ExampleObject__dunder


@pytest.mark.unit
def test_no_duplicate_names():
    """The same decorator function cannot be applied to two names on the same class."""
    with pytest.raises(RuntimeError):

        class DuplicateCheck:
            @cached_property
            def x() -> int:
                return 3

            y = x
