__all__ = ["get_bool_param", "no_body_allowed", "str_to_bool", "get_origin_domain"]

from functools import wraps
from typing import Any
from collections.abc import Callable, Iterable
from urllib.parse import urlparse

from flask import Request, request
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

SAFE_HTTP_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")


def get_bool_param(request: Request, param_name: str, default: bool = False) -> bool:
    """
    Used for properly decoding boolean string parameters into Python bools. We accept case-insensitive true or false.

    NOTE: request.args.get("foo", bool) does not work here; if foo="false" it will return True.
          e.g., (non-empty string -> True)
    """
    value = request.args.get(param_name)
    if value is None:
        return default
    else:
        return str_to_bool(value, param_name)


def str_to_bool(value: str, param_name: str) -> bool:
    case_insensitive_value: str = value.lower()
    if case_insensitive_value == "true":
        return True
    elif case_insensitive_value == "false":
        return False
    else:
        raise ValidationError({param_name: (f"Expected 'true' or 'false'. Instead received '{value}'.")})


def no_body_allowed(func: Callable | None = None, /, methods: Iterable[str] = SAFE_HTTP_METHODS) -> Callable:
    """
    Decorator to be used on MethodView functions if the function does not allow a request body to be passed.

    Can be used with or without parameters.
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapper(*args: list, **kwargs: dict) -> Any:
            if request.method in methods and request.data:
                raise BadRequest("This endpoint does not support a request body")
            return view_func(*args, **kwargs)

        return _wrapper

    if func:
        return decorator(func)
    else:
        return decorator


def get_origin_domain() -> str | None:
    if (source_url := request.headers.get("Origin")) is not None:
        try:
            return urlparse(source_url).netloc or None
        except Exception:
            pass
    return None
