# Standard
import logging
import os
from types import ModuleType
from typing import Any, Union

from peewee import SqliteDatabase

from common.decorators import cached_property
from common.entities import ALL_MODELS, DB

from . import defaults

LOG = logging.getLogger(__name__)


def get_environment() -> str:
    """
    Fetches which configuration schema should be used to read settings from the environment.

    By default, if nothing is set, `cloud` is assumed. This makes sure no production environment is ever
    accidentally misconfigured.
    """
    env = os.environ.get("OBSERVABILITY_CONFIG")

    if env is None:
        env = "cloud"

    if env not in ("local", "test", "minikube", "cloud"):
        raise ValueError(f"Environment must be one of `local`, `test`, `minikube`, `cloud` but got `{env}`")
    return env


SENTINEL = object()


class ConfigClass:
    """Intended essentially a singleton; usage: `from conf import settings`"""

    def __init__(self) -> None:
        self._env_settings: Union[ModuleType, object] = SENTINEL

    @cached_property
    def environment(self) -> str:
        return get_environment()

    def get_modules(self) -> tuple[ModuleType, ...]:
        return (defaults, self.env_settings)

    @property
    def env_settings(self) -> ModuleType:
        if self._env_settings is SENTINEL:
            if self.environment == "local":
                from . import local

                self._env_settings = local

            elif self.environment == "test":
                from . import test

                self._env_settings = test

            elif self.environment == "minikube":
                from . import minikube

                self._env_settings = minikube

            elif self.environment == "cloud":
                from . import cloud

                self._env_settings = cloud

            else:
                raise ValueError(f"Unknown env `{self.environment}`")

        if isinstance(self._env_settings, ModuleType):
            return self._env_settings
        else:
            raise Exception(f"Invalid _env_settings value: {self._env_settings}")

    def __getattr__(self, key: str) -> Any:
        try:
            return getattr(self.env_settings, key)
        except AttributeError as attr_exception:
            try:
                return getattr(defaults, key)
            except AttributeError:
                raise attr_exception from None


settings = ConfigClass()


def init_db() -> None:
    """Initialize the database engine and establish a connection."""
    dbconfig = settings.DATABASE.copy()  # Don't modify config value

    # Get required name & engine parameters
    try:
        EngineKlass = dbconfig.pop("engine")
    except KeyError as e:
        raise ValueError("Missing required `engine` key in DATABASE configuration") from e
    try:
        name = dbconfig.pop("name")
    except KeyError as e:
        raise ValueError("Missing required `name` key in DATABASE configuration") from e

    if DB.obj is None:
        DB.initialize(EngineKlass(name, **dbconfig))
    DB.connect(reuse_if_open=True)
    if EngineKlass is SqliteDatabase:
        DB.create_tables(ALL_MODELS)  # Create the DB tables
