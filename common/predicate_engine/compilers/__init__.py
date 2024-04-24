__all__ = ["compile_schema"]

import logging
from typing import Any

from common.predicate_engine.query import R

from .simple_v1 import compile_simple_v1_schema

LOG = logging.getLogger(__name__)


SCHEMA_MAP = {
    "simple_v1": compile_simple_v1_schema,
}
"""A map of schema version names to a translation function."""


def compile_schema(schema_version: str, rule_data: dict[str, Any]) -> R:
    """Given a Rule entity instance, determine its schema and compile a R object."""
    try:
        compiler_func = SCHEMA_MAP[schema_version]
    except KeyError as e:
        LOG.exception(f"Unsupported rule schema: '{schema_version}'")
        raise Exception(f"Unsupported rule schema: '{schema_version}'") from e
    return compiler_func(rule_data)
