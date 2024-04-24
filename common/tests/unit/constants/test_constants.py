import inspect
import pkgutil
import sys
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Callable, Union

import pytest


def get_constants() -> list[tuple[str, object]]:
    """Walk the constants module and get a map of all values."""
    module_data = {}

    def _walk(module: Union[ModuleType, str] = "common.constants") -> dict[str, ModuleType]:
        try:
            imported_module = import_module(module) if isinstance(module, str) else module
        except (ImportError, ModuleNotFoundError):
            return {}
        module_dict = {f"{imported_module.__name__}": imported_module}
        module_path = imported_module.__file__
        # historical note: On python 3.10, this breaks if pkg_dir is a Path option
        pkg_dir = Path(module_path).parent
        if sys.version_info.minor > 9:
            pkg_dir = str(pkg_dir)

        for _, name, _ in pkgutil.iter_modules((pkg_dir,)):
            pkg_name = f"{imported_module.__name__}.{name}"
            try:
                obj = import_module(pkg_name)
            except (ImportError, ModuleNotFoundError):
                continue
            module_dict[pkg_name] = obj
            module_dict.update(_walk(obj))
        return module_dict

    for name, module in _walk().items():
        values = [x for x in dir(module) if not x.startswith("_")]
        for value_name in values:
            attr_value = getattr(module, value_name)
            if inspect.ismodule(attr_value):
                continue  # Skip modules
            module_data[f"{name}.{value_name}"] = attr_value
    return [(k, v) for k, v in module_data.items()]


inspectors: list[Callable] = [getattr(inspect, x) for x in dir(inspect) if x.startswith("is")]
"""All 'isX' functions in the inspect module."""


@pytest.mark.unit
@pytest.mark.parametrize("name, value", get_constants())
def test_constants(name, value):
    """Validate that constants are actual values, not functions, classes, etc...."""
    for inspector in inspectors:
        assert not inspector(value), f"Value `{name}: {value}` should not have matched {inspector.__name__}"
