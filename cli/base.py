import logging
import os
import sys
from argparse import ArgumentParser
from logging.config import dictConfig
from pathlib import Path
from typing import Any
from collections.abc import Callable

from log_color import ColorFormatter, ColorStripper

from common.entities import DB
from subcommand import SubcommandBase

from . import ARGPARSE_VERSION

LOG = logging.getLogger(__name__)


class ScriptBase(metaclass=SubcommandBase):
    """The ScriptBase class. All scripts should inherit from this class."""

    _main: Callable
    _base_parser: ArgumentParser
    _base_subparsers: ArgumentParser

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs  # Stash them for easy access
        logging_init(level=kwargs.get("log_level", "INFO"), logfile=kwargs.get("logfile"))
        env = self.kwargs.get("environment")
        if env:
            os.environ["OBSERVABILITY_CONFIG"] = env
            LOG.info("Using environment: #c<%s>", env)
        else:
            env_var = os.environ.get("OBSERVABILITY_CONFIG", "cloud")
            LOG.info("Using environment: #c<%s>", env_var)

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        """Setup command line args that are global to all subcommands."""
        parser.add_argument(
            "--environment",
            default=None,
            choices=("local", "minikube", "test", "cloud"),
            help="Force environment; if not set, defaults to the OBSERVABILITY_CONFIG environment variable.",
        )
        parser.add_argument(
            "-l",
            "--log-level",
            default="INFO",
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
            help="Logging level for command output.",
        )
        parser.add_argument(
            "-L", "--logfile", dest="logfile", default=None, help="Location to place a log of the process output"
        )
        parser.add_argument(
            "-V",
            "--version",
            dest="version",
            action="version",
            version=ARGPARSE_VERSION,
            help="Display the version number and exit.",
        )


class DatabaseScriptBase(ScriptBase):
    """A base class for scripts that will initialize a database connection."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        LOG.info("Establishing database connection...")
        from conf import init_db

        try:
            init_db()
        except Exception:
            LOG.exception("#r<\u2718> #y<Error establishing database connection>")
            sys.exit(1)
        LOG.info("#g<\u2714> Established #c<%s> connection to #c<%s>", DB.obj.__class__.__name__, DB.obj.database)


def logging_init(*, level: str, logfile: str | None = None) -> None:
    """Given the log level and an optional logging file location, configure all logging."""
    # Don't bother with a file handler if we're not logging to a file
    handlers = ["console", "filehandler"] if logfile else ["console"]

    # If the main logging level is any of these, set librarys to WARNING
    lib_warn_levels = ("INFO", "WARNING")

    # The base logging configuration
    BASE_CONFIG: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "ConsoleFormatter": {
                "()": ColorFormatter,
                "format": "%(levelname)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "FileFormatter": {
                "()": ColorStripper,
                "format": "%(levelname)-8s: %(asctime)s '%(message)s' %(name)s:%(lineno)s",
            },
        },
        "handlers": {
            "console": {
                "level": level,
                "class": "logging.StreamHandler",
                "formatter": "ConsoleFormatter",
            },
        },
        "loggers": {
            "cli": {
                "handlers": handlers,
                "level": level,
                "propagate": False,
            },
            "common": {
                "handlers": handlers,
                "level": "WARNING" if level in lib_warn_levels else level,
                "propagate": False,
            },
            "common.peewee_extensions.fixtures": {
                "handlers": handlers,
                "level": level,
                "propagate": False,  # Messages in this module won't propogate to the "common" handler
            },
        },
        "root": {"handlers": handlers},
    }

    # If we have a log file, modify the dict to add in the filehandler conf
    # Get logging related arguments & the configure logging
    if logfile:
        logfile_path = Path(logfile).resolve()
        if not logfile_path.parent.exists():
            raise Exception(f"Logfile parent folder does not exist: {logfile_path.parent}")
        if not os.access(logfile_path.parent, os.W_OK):
            raise Exception(f"Logfile parent folder is not writable: {logfile_path.parent}")
        BASE_CONFIG["handlers"]["filehandler"] = {
            "level": level,
            "class": "logging.FileHandler",
            "filename": logfile_path,
            "formatter": "FileFormatter",
        }

    # Setup the loggers
    dictConfig(BASE_CONFIG)
