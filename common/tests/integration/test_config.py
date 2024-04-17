import os
import shutil
from unittest.mock import PropertyMock, patch

import pytest
from flask import Flask

from common.api.flask_ext.config import Config


@pytest.fixture
def flask_app():
    app = Flask(__name__, instance_relative_config=True)
    with patch("conf.ConfigClass.environment", new_callable=PropertyMock) as env_mock:
        env_mock.return_value = "test"  # Force use of test config at observability_api.config.test
        Config(app, config_module="observability_api.config")

    os.makedirs(app.instance_path, exist_ok=True)
    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.mark.integration
def test_get_flask_default_values(flask_app):
    for key in ("SERVER_NAME", "API_PREFIX"):
        try:
            flask_app.config[key]
        except KeyError:
            pytest.fail(f"Config is missing key {key}")


@pytest.mark.integration
def test_get_flask_test_values(flask_app):
    for key in ("PROPAGATE_EXCEPTIONS", "OAUTHLIB_INSECURE_TRANSPORT"):
        try:
            value = flask_app.config[key]
        except KeyError:
            pytest.fail(f"Config is missing key {key}")
        assert value is True, f"Config value `{key}` should be True in test config. Got `{value}`"


@pytest.mark.integration
def test_get_conf_module_value(flask_app):
    """Values from core config are made available on `app.config`"""
    try:
        flask_app.config["DATABASE"]
    except KeyError:
        pytest.fail("Config is missing key DATABASE")


@pytest.mark.integration
def test_no_dunder_methods(flask_app):
    """Dunder methods don't reach Flask config."""
    with pytest.raises(KeyError):
        flask_app.config["__name__"]
