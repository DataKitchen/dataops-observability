import logging
from importlib.metadata import PackageNotFoundError, version
from typing import Any

LOG = logging.getLogger("cli")


def get_version(name: str = "cli") -> str:
    """
    Determine the version of an installed package.

    By default, get_version() always returns the vermin version but the **name** keyword
    argument can be passed to get version info for any installed package.
    """

    try:
        return version(name)
    except PackageNotFoundError:
        return "Development"
    except Exception:
        return "Unknown"


VERSION: str = get_version(name="cli")
ARGPARSE_VERSION: str = f"%(prog)s {VERSION}"
__version__: str = VERSION


def get_argparse_version(name: str = "cli") -> str:
    """
    Return an argparse compatible version string for an installed package.

    By default, get_argparse_version() always returns the vermin version but the **name** keyword
    argument can be passed to get a version string for any installed package.
    """
    return f"%(prog)s {get_version(name)}"


# The modules listing here MUST come after VERSION, ARGPARSE_VERSION, get_argparse_version, and get_version because
# subcommand modules may import from here. Failing to put the module imports last results in an import loop, so don't
# go moving this stuff around ;-)

required: dict[str, Any] = {}
modules: tuple[str, ...] = (
    "cli.entry_points.database_schema",
    "cli.entry_points.dump_fixture",
    "cli.entry_points.gen_events",
    "cli.entry_points.graph_schema",
    "cli.entry_points.load_fixture",
    "cli.entry_points.migration_check",
    "cli.entry_points.service_account_key",
    "cli.entry_points.shell",
    "cli.entry_points.init",
)

for module in modules:
    try:
        locals()[module] = __import__(module)
    except ImportError as err:
        required[module.split(".")[-1]] = err


__all__: tuple[str, ...] = (
    "__version__",
    "ARGPARSE_VERSION",
    "get_argparse_version",
    "get_version",
    "modules",
    "VERSION",
)
