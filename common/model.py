__all__ = ["walk", "create_all_tables"]

import inspect
import logging
import os
import pkgutil
from contextlib import suppress
from importlib import import_module
from types import ModuleType
from typing import Optional

from peewee import Database, Model, SchemaManager

from common import entities
from common.entities import Component

LOG = logging.getLogger(__name__)


def walk(module: Optional[ModuleType] = None) -> dict[str, Model]:
    """
    Recursively scans a module for all PeeWee model classes. Defaults to `common.entities` but can scan any module.

    >>> from common.model import walk
    >>> model_map = walk()
    >>> model_map['User']
    >>> <class 'asset_model.general.user.User'>
    """
    base_classes: dict[str, Model] = {}
    if module is None:
        module = entities

    try:
        module_path = module.__file__
    except AttributeError:
        module_path = inspect.getfile(module)

    if not module_path:
        return base_classes

    # Snag the package directory for the module
    pkg_dir = os.path.dirname(module_path)

    for _, name, _ in pkgutil.iter_modules([pkg_dir]):
        pkg_name = f"{module.__name__}.{name}"
        try:
            obj = import_module(pkg_name)
        except ImportError:
            continue
        for dir_name in dir(obj):
            if dir_name.startswith("_"):
                continue
            dir_obj = getattr(obj, dir_name)
            if (
                dir_obj is Model
                or dir_obj is entities.BaseModel
                or dir_obj is entities.BaseEntity
                or dir_obj is entities.ActivableEntityMixin
                or dir_obj is entities.AuditEntityMixin
            ):
                continue  # Skip if it's just an import of the model base class or base entity class
            try:
                if issubclass(dir_obj, Model) and (dir_obj is Component or not issubclass(dir_obj, Component)):
                    base_classes[f"{dir_obj.__module__}.{dir_obj.__name__}"] = dir_obj
                    LOG.debug("Adding %s", dir_obj)
            except TypeError:
                pass
            except Exception:
                LOG.exception("Error adding class %s", dir_obj)

        if obj:
            with suppress(ImportError, TypeError):
                base_classes.update(walk(module=obj))
    return base_classes


def create_all_tables(database: Database, safe: bool = False) -> None:
    """Creates all entities tables and constraints on the given database."""
    with database.bind_ctx(entities.ALL_MODELS):
        database.create_tables(entities.ALL_MODELS, safe=safe)

        # All deferred foreign key fields constraints should be created here

        # Component should have the FK created, but its children shouldn't
        SchemaManager(Component).create_foreign_key(Component.created_by)
        for entity in entities.ALL_MODELS:
            if issubclass(entity, entities.AuditEntityMixin) and not issubclass(entity, Component):
                SchemaManager(entity).create_foreign_key(entity.created_by)
