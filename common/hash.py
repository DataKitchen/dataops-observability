from collections.abc import Iterable, Mapping
from decimal import Decimal
from hashlib import blake2b
from typing import Any
from typing import Iterable as IterableType
from typing import Mapping as MappingType
from typing import Union

SALT = b"e1e10042"


def hash_iterable(iterable: IterableType[Any]) -> bytes:
    """Hash an iterable object"""
    hash_func = blake2b(salt=SALT, digest_size=32)
    _update_hash = hash_func.update  # Stash in local context for faster lookups
    _update_hash(iterable.__class__.__name__.encode("utf-8"))
    for item in iterable:
        _update_hash(calculate_hash(item))
    return hash_func.digest()


def hash_number(number: Union[int, float, complex, Decimal]) -> bytes:
    """Hash a numerical object instance"""
    hash_func = blake2b(salt=SALT, digest_size=32)
    hash_func.update(repr(number).encode("utf-8"))
    return hash_func.digest()


def hash_mapping(map_obj: MappingType[Any, Any]) -> bytes:
    """Hash a key/value mapping"""
    hash_func = blake2b(salt=SALT, digest_size=32)
    _update_hash = hash_func.update
    _update_hash(map_obj.__class__.__name__.encode("utf-8"))
    for k, v in map_obj.items():
        _update_hash(calculate_hash(k))
        _update_hash(calculate_hash(v))
    return hash_func.digest()


def calculate_hash(obj: Any) -> bytes:
    """Generate a hash value from an object."""
    if isinstance(obj, str):
        return obj.encode("utf-8")
    elif isinstance(obj, (int, float, complex, Decimal)):
        return hash_number(obj)
    elif isinstance(obj, Mapping):
        return hash_mapping(obj)
    elif isinstance(obj, Iterable):
        return hash_iterable(obj)
    elif isinstance(obj, (bytes, memoryview)):
        hash_func = blake2b(salt=SALT, digest_size=32)
        hash_func.update(obj)
        return hash_func.digest()
    else:
        hash_func = blake2b(salt=SALT, digest_size=32)
        _update_hash = hash_func.update
        _update_hash(str(obj).encode("utf-8"))
        try:
            _update_hash(obj.__class__.__name__.encode("utf-8"))
        except Exception:
            pass  # OK to ignore; useful when present
        try:
            _update_hash(obj.__name__.encode("utf-8"))
        except Exception:
            pass  # OK to ignore; useful when present
        return hash_func.digest()


def generate_key(*args: Any) -> str:
    """Generate a hash value from one or more arguments. Useful for generating keys for caching."""
    hash_func = blake2b(salt=SALT, digest_size=32)
    _update_hash = hash_func.update
    for obj in args:
        if isinstance(obj, (bytes, memoryview)):
            _update_hash(obj)
        else:
            _update_hash(calculate_hash(obj))
    return hash_func.hexdigest()
