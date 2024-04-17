from collections import OrderedDict
from pathlib import PurePosixPath, PureWindowsPath

import pytest

from common.hash import generate_key


class WrappedStr:
    """Custom object for testing hashing."""

    def __init__(self, _str):
        self._str = _str

    def __str__(self):
        return self._str


@pytest.mark.unit
def test_hash_generate_key():
    """Make sure key generation is deterministic"""
    expected = "2f7e1698086dca7d08d76ae2535b7d75ccda047d08b05f8fc62177f950b765d5"
    actual = generate_key("a", "b", "c", 1, 2, 3)
    assert expected == actual


@pytest.mark.unit
def test_hash_dict():
    """Dictionary objects can be used to generate keys."""
    expected = "2a4d60dba8ffa8901cdc2563abe4e016b08e325f5fa528fe0660ec54562b3ee2"
    actual = generate_key("a", "b", "c", {"foo": "bar"})
    assert expected == actual


@pytest.mark.unit
def test_hash_ordered_dict():
    """Ordered dictionary objects can be used to generate keys."""
    expected = "6adbe1f7f924b1e5c526d393db1b186fa123049f7646f6d77cb5a19996b801e0"
    actual = generate_key("a", "b", "c", OrderedDict({"foo": "bar"}))
    assert expected == actual


@pytest.mark.unit
def test_hash_generate_key_two_my_objects():
    """Non-scalar objects with different __str__ representations generate unique keys."""
    one, two = WrappedStr("one"), WrappedStr("two")
    assert str(one) != str(two)
    assert generate_key(one) != generate_key(two)


@pytest.mark.unit
def test_hash_list():
    """List objects can be used to generate keys."""
    expected = "1fcd15a724b66b0ec51f44306f5aed8c5de2cfb3326b792ec371c7b7b275bcd4"
    actual = generate_key("a", "b", "c", ["foo", "bar"])
    assert expected == actual


@pytest.mark.unit
def test_hash_bytes():
    """Bytes can be used to generate keys."""
    expected = "4e91c239fada0e4aa32b0dff5c6fa2e9bfad8508a23ed79d2bb185f1b80666f5"
    actual = generate_key(b"fourtytwo")
    assert expected == actual


@pytest.mark.unit
def test_hash_recursion():
    """Key generation recurses through hashmap values."""
    expected = "246235acb79e2fe5976c894375ad310de072a3306dd3700f854453f8072802c3"
    actual = generate_key("a", "b", "c", {"foo": ("bar", "baz")}, memoryview(b"seventy-minus-one"))
    assert expected == actual


@pytest.mark.unit
def test_hash_path_obj_different():
    """Identical paths for a Windows & Posix don't generate the same hash."""
    win_path = PureWindowsPath("c:\\foo\\bar")
    posix_path = PurePosixPath(win_path.as_posix())

    win_key = generate_key(win_path)
    posix_key = generate_key(posix_path)

    assert win_key != posix_key
