import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    os.environ["OBSERVABILITY_CONFIG"] = "test"
