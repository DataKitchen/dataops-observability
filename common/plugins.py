import logging
from collections import defaultdict
from typing import Optional, Callable

LOG = logging.getLogger(__name__)

class PluginManager:

    registry = defaultdict(list)

    @classmethod
    def load_all(cls, hook_name: str, *args, **kwargs):

        try:
            import observability_plugins
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
    def register(cls, hook_name: str, callback: Optional[Callable] = None):
        try:
            if callback:
                cls.registry[hook_name].append(callback)
                LOG.info("Registered plugin '%s' for '%s' hook", callback.__name__, hook_name)
            else:
                def decorate(callback):
                    cls.register(hook_name, callback)
                    return callback

                return decorate
        finally:
            LOG.info(cls.registry)
