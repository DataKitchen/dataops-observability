__all__ = [
    "is_ready",
    "set_ready",
    "block_until_ready_and_exit",
    "get_args_handler",
    "readiness_check_wrapper",
    "NotReadyException",
]

import logging
import os
import sys
import tempfile
import time
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from typing import NoReturn
from collections.abc import Generator
from collections.abc import Callable

LOG = logging.getLogger(__name__)

FILE_NAME = "observability_readyz"
"""Name of the file that will be created into the temp dir to mark the service as ready."""

POLLING_SLEEP_SECONDS = 0.1
"""How many seconds to wait between each attempt to check the service readiness."""

FAIL_EXIT_CODE = 1
"""Exit code to be used then the service is not ready."""


class NotReadyException(Exception):
    """Raised when the service shouldn't be marked as ready."""


def _get_mark_file_path() -> str:
    return os.path.join(tempfile.gettempdir(), FILE_NAME)


def set_ready() -> None:
    """Mark the service as ready by adding a PID file to the temp dir."""
    with open(_get_mark_file_path(), "w") as mark_file:
        mark_file.write(str(os.getpid()))


def is_ready() -> bool:
    """Checks the existence of the readiness mark file."""
    return os.path.exists(_get_mark_file_path())


@contextmanager
def readiness_check_wrapper() -> Generator[None, None, None]:
    """
    Context Manager that marks the service as ready when the inner code is executed without exceptions. Re-raises
    the exception otherwise.
    """
    try:
        yield
    except Exception as e:
        LOG.warning("Service is NOT READY: [%s]", e)
        raise
    else:
        set_ready()
        LOG.info("Service marked as READY")


def block_until_ready_and_exit(timeout: int) -> NoReturn:
    """
    Wait for the service to be marked as ready until the timeout is not reached. Terminates the process in either case.
    Exit code is 0 when the service is ready, 1 otherwise.

    :param timeout: Total seconds to wait
    """
    started = time.time()
    while time.time() - started < timeout:
        if is_ready():
            LOG.info("Readiness probe SUCCEEDED")
            sys.exit()
        else:
            time.sleep(POLLING_SLEEP_SECONDS)
    LOG.info("Readiness probe FAILED")
    sys.exit(FAIL_EXIT_CODE)


def get_args_handler(timeout: int) -> Callable:
    """
    Build a handler to be used with `common.argparse`. When --check-ready is used, it checks the main process
    readiness and exits.
    """

    def handler(parser: ArgumentParser) -> Generator[None, Namespace, None]:
        parser.add_argument("--check-ready", help="Check the main process readiness and exit", action="store_true")
        args = yield
        if args.check_ready:
            block_until_ready_and_exit(timeout)

    return handler
