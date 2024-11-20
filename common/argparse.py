"""
Manages a default ArgumentParser for the application, allowing handlers to be attached. These handlers are responsible
for adding the relevant arguments, checking their usage and act accordingly.

A handler must be a generator function that receives the ArgumentParser instance as an argument, adds its relevant
arguments and then yields. It will be sent the parsing result instance for processing.
"""

import argparse
from collections.abc import Callable

DEFAULT_ARG_PARSER: argparse.ArgumentParser = argparse.ArgumentParser()
"""Default ArgumentParser instance."""

REGISTERED_HANDLERS: list[Callable] = []
"""Handlers registry."""


def add_arg_handler(handler: Callable) -> None:
    """Add a handler to the registry."""
    if handler not in REGISTERED_HANDLERS:
        REGISTERED_HANDLERS.append(handler)


def handle_args() -> None:
    """Call all handlers sequentially for argument setup, then send the parsed args to each handler for processing."""
    generators = []
    for handler in REGISTERED_HANDLERS:
        gen = handler(DEFAULT_ARG_PARSER)
        next(gen)
        generators.append(gen)
    args = DEFAULT_ARG_PARSER.parse_args()
    for gen in generators:
        try:
            gen.send(args)
        except StopIteration:
            pass
