import os
import re
import textwrap
from argparse import ArgumentParser, ArgumentTypeError
from typing import Optional
from uuid import UUID

from log_color.colors import ColorStr


def uuid_type(arg: str) -> UUID:
    """Argument type converter for UUID values."""
    try:
        uuid_arg = UUID(arg)
    except Exception as e:
        raise ArgumentTypeError(f"Invalid UUID value: `{arg}`") from e
    else:
        return uuid_arg


def slice_type(arg: str) -> slice:
    """Convert an argument to a slice; for simplicity, disallow negative slice values and steps."""

    def _int_or_none(val: str) -> Optional[int]:
        if not val:
            return None
        else:
            return int(val)

    try:
        parts = [_int_or_none(x) for x in arg.split(":")]
    except (TypeError, ValueError) as e:
        raise ArgumentTypeError(f"Invalid SLICE value: `{arg}`") from e

    if len(parts) > 3 or len(parts) < 2:
        raise ArgumentTypeError(f"Invalid SLICE value: `{arg}`")

    try:
        slice_val = slice(*parts)
    except ValueError as e:
        raise ArgumentTypeError(f"Invalid SLICE value: `{arg}`") from e

    if slice_val.step and slice_val.step != 1:
        raise ArgumentTypeError(f"Invalid SLICE value; 'step' value must be 1: `{arg}`")
    if slice_val.start and (slice_val.start != abs(slice_val.start)):
        raise ArgumentTypeError(f"Invalid SLICE value; negative 'start' values are not allowed: `{arg}`")
    if slice_val.stop and (slice_val.stop != abs(slice_val.stop)) and slice_val.stop != -1:
        raise ArgumentTypeError(f"Invalid SLICE value; negative 'stop' values beyond -1 are not allowed: `{arg}`")

    return slice_val


def slice_to_str(arg: slice) -> str:
    """Convert a slice value to a string representation."""
    if arg.start is None and arg.step is None:
        return f"[:{arg.stop}]"
    if arg.step is None and arg.stop is None:
        return f"[{arg.start}:]"
    parts = (
        str(arg.start) if arg.start is not None else "",
        str(arg.stop) if arg.stop is not None else "",
        str(arg.step) if arg.step is not None else "",
    )
    joined_value = ":".join(parts)
    return f"[{joined_value.rstrip(':')}]"


def generate_subcommand_description(subparsers: ArgumentParser) -> str:
    """
    Format the helptext for a root parser by snagging the description for all of the given subparsers.

    Sample output::

        Subcommands:
         sub-command    Description for sub-command
         other-command  Description for other-command
    """
    if ColorStr.color_supported():
        info_list = ["\033[96mSubcommands:\033[0m"]
    else:
        info_list = ["Subcommands:"]

    base_indent = 4
    subparser_choices = getattr(subparsers, "choices", {}) or {}
    if not subparser_choices:
        return ""

    indent_value = max([len(x) for x in subparser_choices.keys()]) + 4 + base_indent
    for key, val in sorted(subparser_choices.items(), key=lambda x: x[0]):
        subcmd_name = key + "  "
        if ColorStr.color_supported():
            subcmd_name = f"\033[92m{subcmd_name}\033[0m"
        initial_indent = " " * base_indent
        post_space = " " * (indent_value - len(subcmd_name) - base_indent)
        desc = re.sub(r"[ ]{2,}", " ", (val.description or "").replace("\n", " "))
        desc = ("\n" + (" " * indent_value)).join(textwrap.wrap(desc))
        info_list.append(f"{initial_indent}{subcmd_name}{post_space}{desc}")

    return os.linesep.join(info_list)
