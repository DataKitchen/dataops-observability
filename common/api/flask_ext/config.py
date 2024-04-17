__all__ = ["Config"]
import os
from typing import Optional

from flask import Flask

from conf import settings


class Config:
    """
    Reads a configuration module for a module that matches the ENV configuration setting.

    The config_module passed to the Config plugin should be the module where configuration values are stored. This is
    combined with the value of the flask ENV setting. i.e. if config_module="foo.bar" and flask ENV is "production"
    then the configuration will load "foo.bar.production"
    """

    def __init__(self, app: Optional[Flask] = None, config_module: str = ""):
        if not config_module:
            raise ValueError("You must provide a 'config_module' to the Config extension")
        self.app = app
        self.config_module = config_module
        if app is not None:
            self.init_app()

    def init_app(self) -> None:
        if self.app is not None:
            config = self.app.config  # Stash locally to avoid repeated attribute lookups

            # Pull backend configurations. These are values that are part of the top-level configuration but not
            # necessarily flask specific. TODO: I'm assuming they may be useful but it might be just as reasonable to
            # assume we'll never need them in the flask context. Open to discussion.
            for module in settings.get_modules():
                config.update({k: v for k, v in module.__dict__.items() if not k.startswith("__")})

            # Flask configuration module names
            default_module_name = f"{self.config_module}.defaults"
            module_name = f"{self.config_module}.{settings.environment}"

            # Pull default configurations first
            config.from_object(default_module_name)

            # Pull the specified configuration module (settings in this module take precedence)
            config.from_object(module_name)

            if config.get("OAUTHLIB_INSECURE_TRANSPORT") is True:
                os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
