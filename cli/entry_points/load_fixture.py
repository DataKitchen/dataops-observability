import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from cli.base import DatabaseScriptBase
from common.peewee_extensions.fixtures import load_file, load_folder

LOG = logging.getLogger(__name__)


class LoadFixture(DatabaseScriptBase):
    """Load fixture data into the database."""

    subcommand: str = "load-fixture"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Load a fixture file or a folder of fixture files."
        parser.usage = "$ cli load-fixture [PATH]"
        parser.add_argument("PATH", nargs="?", type=Path)
        parser.add_argument(
            "--disable-recursion",
            action="store_true",
            dest="disable_recursion",
            help="Disable recursing into subfolders to look for fixture files",
        )
        parser.add_argument(
            "--create-only",
            action="store_true",
            dest="create_only",
            help="Fail instead of overwriting existing data",
        )

    def subcmd_entry_point(self) -> None:
        fixture_path: Path = self.kwargs["PATH"].resolve()
        recursive = False if self.kwargs.get("disable_recursion") else True
        overwrite = False if self.kwargs.get("create_only") else True
        if fixture_path.is_dir():
            LOG.info("Using fixture files in: #c<%s>", fixture_path)
            load_folder(fixture_path, overwrite=overwrite, recursive=recursive)
        elif fixture_path.is_file():
            LOG.info("Using fixture file: #c<%s>", fixture_path)
            load_file(fixture_path, overwrite=overwrite)
        else:
            LOG.error("#r<Invalid fixture path:> #y<%s>", fixture_path)
            sys.exit(1)

        LOG.info("#g<\u2714 Finished!>")
        sys.exit(0)
