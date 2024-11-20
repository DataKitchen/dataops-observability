import logging
from collections import defaultdict
from typing import Any
from collections.abc import Callable

LOG = logging.getLogger(__name__)

PLUGIN_CALLBACK = Callable[[Any, Any], None]


class PluginManager:
    registry = defaultdict[str, list[PLUGIN_CALLBACK]](list)

    @classmethod
    def load_all(cls, hook_name: str, *args: Any, **kwargs: Any) -> None:
        try:
            import observability_plugins  # noqa: F401
        except ImportError:
            LOG.debug("No available plugins, continuing without")

        for plugin_loader in cls.registry[hook_name]:
            try:
                plugin_loader(*args, **kwargs)
            except Exception:
                LOG.exception("Failed to load plugin '%s' for '%s' hook", plugin_loader.__name__, hook_name)
                raise
            else:
                LOG.info("Successfully loaded plugin '%s' for '%s' hook", plugin_loader.__name__, hook_name)

    @classmethod
    def register(cls, hook_name: str) -> Callable[[PLUGIN_CALLBACK], PLUGIN_CALLBACK]:
        def decorate(callback: PLUGIN_CALLBACK) -> PLUGIN_CALLBACK:
            cls.registry[hook_name].append(callback)
            LOG.info("Registered plugin '%s' for '%s' hook", callback.__name__, hook_name)
            return callback

        return decorate
