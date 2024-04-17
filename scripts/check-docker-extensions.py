#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import NoReturn

"""
Turns out, kics and others care about the dockerfile name extension and its case.
this is just a minor check to ensure that new files have the correct case, as it
will be very unclear when things go wrong. This script may be useful to expand
to other hidden foot-guns like that.

This script is meant to be used with pre-commit. For pre-commit, that means files
are all passed on the command-line.
"""


def main() -> NoReturn:
    invalid_files: list[Path] = []
    for file in sys.argv[1:]:
        path: Path = Path(file)
        if path.suffix.lower() == ".dockerfile":
            if str(path.suffix) != ".dockerfile":
                invalid_files.append(path)

    if invalid_files:
        print(
            "The build system scanners expect a lowercase dockerfile extension. Offenders: "
            + ", ".join(str(f) for f in invalid_files),
            file=sys.stderr,
        )
        sys.exit(1)

    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
