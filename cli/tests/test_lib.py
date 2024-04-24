from argparse import ArgumentTypeError
from uuid import UUID

import pytest

from cli import lib


@pytest.mark.unit
@pytest.mark.parametrize("uuid_value", ("f2c07017-5a20-42a4-a3b3-401312068fb7", "f2c070175a2042a4a3b3401312068fb7"))
def test_uuid_type(uuid_value):
    result = lib.uuid_type(uuid_value)
    assert isinstance(result, UUID)


@pytest.mark.unit
@pytest.mark.parametrize("uuid_value", ("x2c07017-5a20-42a4-a3b3-401312068zm3", "12068fb7"))
def test_uuid_type_bad_value_raises(uuid_value):
    with pytest.raises(ArgumentTypeError):
        lib.uuid_type(uuid_value)


@pytest.mark.unit
@pytest.mark.parametrize("slice_value", ("10:100", "1:10", "1:1:1", "10:-1:1", "42:", "::1", "1::", "1:1:"))
def test_slice_type(slice_value):
    result = lib.slice_type(slice_value)
    assert isinstance(result, slice)


@pytest.mark.unit
@pytest.mark.parametrize("slice_value", ("10", "10:-2", "1:2:2"))
def test_slice_type_bad_value_raises(slice_value):
    with pytest.raises(ArgumentTypeError):
        lib.slice_type(slice_value)


@pytest.mark.unit
@pytest.mark.parametrize(
    "expected_pairs",
    (
        (slice(1, None, None), "[1:]"),
        (slice(1, 1, None), "[1:1]"),
        (slice(1, 1, 1), "[1:1:1]"),
        (slice(1, 4, 1), "[1:4:1]"),
        (slice(1, 4), "[1:4]"),
        (slice(1, None, 1), "[1::1]"),
        (slice(None, None, 1), "[::1]"),
    ),
)
def test_slice_to_str(expected_pairs):
    slice_obj, expected_str = expected_pairs
    assert lib.slice_to_str(slice_obj) == expected_str
