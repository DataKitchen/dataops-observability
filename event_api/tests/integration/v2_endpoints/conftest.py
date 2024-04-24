import os
import shutil
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from common.api.flask_ext.authentication import ServiceAccountAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.database_connection import DatabaseConnection
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.auth.keys.service_key import generate_key
from common.entities import DB, Company, Organization, Project
from conf import init_db
from event_api.routes import build_v2_routes


@pytest.fixture
def event_time():
    return datetime(2022, 5, 25, 19, 56, 52, 759419, tzinfo=timezone.utc)


@pytest.fixture
def base_event_dict(event_time) -> dict[str, object]:
    return {
        "external_url": None,
        "event_timestamp": event_time.isoformat(),
        "metadata": {"key": "value"},
        "payload_keys": ["p1", "p2"],
    }


@pytest.fixture
def batch_pipeline_dict():
    return {
        "batch_key": "batch component key",
        "run_key": "run key",
    }


@pytest.fixture
def dataset_dict():
    return {
        "dataset_key": "dataset component key",
    }


@pytest.fixture
def component(batch_pipeline_dict):
    return {
        "batch_pipeline": batch_pipeline_dict,
    }


@pytest.fixture(autouse=True)
def test_db():
    init_db()
    yield
    DB.close()


@pytest.fixture
def kafka_producer() -> MagicMock:
    kafka_producer = MagicMock()
    # Context manager also returns the same mock
    kafka_producer.__enter__.return_value = kafka_producer
    return kafka_producer


@pytest.fixture
def flask_app(kafka_producer):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    Config(app, config_module="event_api.config")
    build_v2_routes(app, prefix="events")
    ExceptionHandling(app)
    DatabaseConnection(app)
    ServiceAccountAuth(app)

    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture(autouse=True)
def kafka_class_mock(kafka_producer):
    with patch("event_api.endpoints.v2.event_view.KafkaProducer", return_value=kafka_producer):
        yield


@pytest.fixture
def company():
    return Company.create(name="ExampleCompany")


@pytest.fixture
def organization(company):
    return Organization.create(name="ExampleOrganization", company=company)


@pytest.fixture
def project(organization):
    return Project.create(name="ExampleProject", active=True, organization=organization)


@pytest.fixture
def service_key(project, flask_app):
    return generate_key(allowed_services=[flask_app.config["SERVICE_NAME"]], project=project).encoded_key


@pytest.fixture
def service_account_key_headers(service_key):
    return {ServiceAccountAuth.header_name: service_key}


@pytest.fixture
def headers(service_account_key_headers):
    return service_account_key_headers


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        yield client
