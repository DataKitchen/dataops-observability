__all__ = ["Logging"]
from logging.config import dictConfig

from flask.logging import default_handler

from common.api.flask_ext.base_extension import BaseExtension
from common.logging import JsonFormatter


class Logging(BaseExtension):
    def init_app(self) -> None:
        # We're handling configuration so remove the default handler; dictConfig will add our handler to the app logger
        self.app.logger.removeHandler(default_handler)

        # On production, we use INFO level. For debug/testing, we use DEBUG level
        if self.app.config["DEBUG"] or self.app.config["TESTING"]:
            level = "DEBUG"
        else:
            level = "INFO"

        # We use the json log formatter in all the environments
        handlers = ["json"]

        LOG_CONFIG: dict[str, object] = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "JsonFormatter": {"()": JsonFormatter},
                "simple": {"format": "[%(levelname)s] %(message)s  [%(name)s:%(lineno)s]"},
            },
            "handlers": {
                "json": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "JsonFormatter",
                },
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
            },
            # The following list specifies all of the packages from which we wish to dispatch logs. If we add another
            # api or library, it would be a good idea to declare it here. You can also change the log level for
            # submodules; for example to have `foo.bar` only log at the CRITICAL level while having ``foo`` otherwise
            # log at the debug level:
            #     "foo.bar": {"handlers": handlers, "level": "CRITICAL"},
            #     "foo": {"handlers": handlers, "level": "DEBUG"},
            # You may also wish to add loggers for libraries or other dependencies. Typically the log level for those
            # is set to a higher level like "WARNING" to keep them from being overly chatty, but this is up to the
            # discretion of the developer.
            # Please do use the `handlers` variable when specifying handlers; this variable differs automatically based
            # on the deployment environment.
            "loggers": {
                self.app.logger.name: {"handlers": handlers, "level": level, "propagate": False},
                "app": {"handlers": handlers, "level": level, "propagate": False},
                "observability_api": {"handlers": handlers, "level": level, "propagate": False},
                "observability": {"handlers": handlers, "level": level, "propagate": False},
                "conf": {"handlers": handlers, "level": level, "propagate": False},
                "common": {"handlers": handlers, "level": level, "propagate": False},
                "event_api": {"handlers": handlers, "level": level, "propagate": False},
                "flask": {"handlers": handlers, "level": "WARNING", "propagate": False},
                "peewee": {"handlers": handlers, "level": "WARNING", "propagate": False},
                "urllib3": {"handlers": handlers, "level": "WARNING", "propagate": False},
            },
            "root": {"handlers": handlers},
        }
        dictConfig(LOG_CONFIG)
