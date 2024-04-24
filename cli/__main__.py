import argparse
import sys
import traceback

from log_color.colors import ColorStr

import cli
from cli.base import ScriptBase
from cli.lib import generate_subcommand_description


def main() -> None:
    root_parser = ScriptBase._base_parser
    root_parser.prog = "cli"
    rsubparsers = ScriptBase._base_subparsers
    rsubparsers.formatter_class = argparse.RawDescriptionHelpFormatter
    root_parser.description = generate_subcommand_description(rsubparsers)

    root_parser.formatter_class = argparse.RawDescriptionHelpFormatter
    if cli.required:
        root_parser.epilog = "disabled Commands:\n"
        for module, ierr in cli.required.items():
            root_parser.epilog += f" - {module} subcommand requires module {str(ierr).split(' ')[-1]}\n"

    try:
        ScriptBase._main()
    except KeyboardInterrupt:
        msg = "\u2717 Operation canceled by user"
        if ColorStr.color_supported():
            msg = f"\n\033[91m{msg}\033[0m\n"
        sys.stderr.write(msg)
        sys.exit(1)
    except Exception as ex:
        msg = f"\u2717 Error Running Script:\n{str(ex)}\n{traceback.format_exc()}"
        if ColorStr.color_supported():
            msg = f"\n\033[91m{msg}\033[0m\n"
        sys.stderr.write(msg)
        sys.exit(1)

    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
