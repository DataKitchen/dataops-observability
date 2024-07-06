import code
import logging
import readline  # noqa: F401 Appears unused but is required for the interactive shell to function
import sys
from argparse import ArgumentParser
from typing import Callable, Optional

from cli.base import DatabaseScriptBase
from common.entities import *
from conf import settings

LOG = logging.getLogger(__name__)


class Shell(DatabaseScriptBase):
    """Open an interactive shell with a connected database."""

    subcommand: str = "shell"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Open an interactive shell."
        parser.usage = "$ cli shell"

    def subcmd_entry_point(self) -> None:
        current_vars = globals().copy()
        current_vars.update(locals())

        LOG.info("#g<Interactive Console>")
        LOG.info("Database Engine: #b<%s.%s>", DB.obj.__module__, DB.obj.__class__.__name__)
        LOG.info("Database Name: #b<%s>", settings.DATABASE.get("name", "Unknown"))
        LOG.info(
            "#dg<Tips:>\n"
            "          * #b<conf.settings> is imported\n"
            "          * #b<common.entities.*> is imported\n"
            "          * Type #b<help> to see available tools\n"
            "          * #b<ALL_MODELS> lists available model classes\n"
            "          * Press #r<Ctrl-D> to exit at any time\n"
        )

        start_ipython: Optional[Callable] = None

        try:
            from IPython import start_ipython
        except ImportError:
            pass

        if start_ipython:
            # If you don't set argv to an empty value here, iPython will attempt to use the arguments passed to the
            # cli command and mayhem will ensue.
            start_ipython(argv=[], user_ns=current_vars)
        else:
            shell = code.InteractiveConsole(current_vars)
            shell.interact()

        sys.exit(0)
