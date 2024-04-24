import pytest

from cli import modules


@pytest.mark.unit
@pytest.mark.parametrize("module", modules)
def test_entry_point_import(module):
    """Validates that all specified entry points can be imported without errors."""
    try:
        __import__(module)
    except ImportError as e:
        raise AssertionError(f"Unable to import entry point: {module}") from e
    except Exception as e:
        raise AssertionError(f"Unexpected error importing entry point: {module}") from e
