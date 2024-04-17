from http import HTTPStatus

import pytest
from flask import Flask

from common.api.flask_ext.health import Health
from common.kubernetes import NotReadyException


@pytest.mark.integration
def test_readiness(client, readiness_check_callback):
    assert client.get("/test/readyz").status_code == HTTPStatus.OK
    readiness_check_callback.assert_called_once()


@pytest.mark.integration
def test_readiness_not_ready(client, readiness_check_callback):
    readiness_check_callback.side_effect = NotReadyException()
    assert client.get("/test/readyz").status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    readiness_check_callback.assert_called_once()


@pytest.mark.integration
def test_liveliness(client):
    assert client.get("/test/livez").status_code == HTTPStatus.OK


@pytest.mark.integration
def test_prefix_required():
    app = Flask(__name__)
    with pytest.raises(ValueError):
        Health(app, "", lambda: None)
