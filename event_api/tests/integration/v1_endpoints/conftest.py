import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from flask import Flask

from common.api.flask_ext.authentication import ServiceAccountAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.database_connection import DatabaseConnection
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.auth.keys.service_key import generate_key
from common.entities import DB, Company, Organization, Project
from common.events.v1 import ApiRunStatus, MessageEventLogLevel, TestgenIntegrationVersions, TestStatuses
from conf import init_db
from event_api.routes import build_v1_routes


@dataclass
class DatabaseCtx:
    project: Project
    company: Company
    organization: Organization
    service_key: str


@pytest.fixture
def predictable_datetime():
    return datetime(2022, 5, 25, 19, 56, 52, 759419, tzinfo=timezone.utc)


@pytest.fixture
def base_schema(predictable_datetime) -> dict[str, object]:
    return {
        "pipeline_key": "154a9bdd-ab27-4efb-8f57-42df2f69b103",
        "pipeline_name": "My Pipeline",
        "run_key": "run-correlation",
        "event_timestamp": predictable_datetime.isoformat(),
        "metadata": {"key": "value"},
        "external_url": "https://example.com",
    }


@pytest.fixture
def messagelog_schema(base_schema) -> dict[str, object]:
    base_schema["task_key"] = "Foo"
    base_schema["log_level"] = MessageEventLogLevel.INFO.name
    base_schema["message"] = "Test Message Please Ignore"
    return base_schema


@pytest.fixture
def metriclog_schema(base_schema) -> dict[str, object]:
    base_schema["task_key"] = "Foo"
    base_schema["metric_key"] = "key"
    base_schema["metric_value"] = 10.12
    return base_schema


@pytest.fixture
def test_outcomes_data(base_schema) -> dict[str, object]:
    test_outcomes_data = {
        "task_key": "Foo",
        "test_outcomes": [
            {"name": "full-test", "status": TestStatuses.PASSED.name, "description": "Hello"},
            {"name": "no-description", "status": TestStatuses.FAILED.name},
        ],
    }
    yield {**base_schema, **test_outcomes_data}


@pytest.fixture
def test_outcomes_data_with_integration(test_outcomes_data) -> dict[str, object]:
    test_outcomes_data["component_integrations"] = {
        "integrations": {
            "testgen": {
                "version": TestgenIntegrationVersions.V1.value,
                "database_name": "redshift_db",
                "connection_name": "redshift_db_con",
                "tables": {
                    "include_list": ["table1"],
                    "include_pattern": "t.*",
                    "exclude_pattern": ".*private.*",
                },
                "schema": "schema1",
                "table_group_configuration": {
                    "group_id": UUID("9f0fa7b8-8c58-4e5c-ae02-d3cb8504a22e"),
                    "project_code": "topsecretproject",
                    "uses_sampling": True,
                    "sample_percentage": "50.0",
                    "sample_minimum_count": 30,
                },
            },
        },
    }
    for to in test_outcomes_data["test_outcomes"]:
        to["integrations"] = {
            "testgen": {
                "table": "table1",
                "test_suite": "testsuite1",
                "version": TestgenIntegrationVersions.V1.value,
                "test_parameters": [
                    {
                        "name": "parameter1",
                        "value": 3.14,
                    },
                    {
                        "name": "parameter2",
                        "value": "a string",
                    },
                ],
                "columns": ["c1"],
            }
        }
    yield test_outcomes_data


@pytest.fixture
def status_schema(base_schema) -> dict[str, object]:
    base_schema["status"] = ApiRunStatus.RUNNING.name
    return base_schema


# TODO: Replace with actual Kafka service instead of mock
@pytest.fixture
def kafka_producer() -> MagicMock:
    kafka_producer = MagicMock()
    # Context manager also returns the same mock
    kafka_producer.__enter__.return_value = kafka_producer
    yield kafka_producer


def patch_datetime(default_timestamp):
    with patch("event_api.endpoints.v1.event_view.datetime") as dt:
        dt.now.return_value = default_timestamp
        yield


@pytest.fixture
def flask_app(kafka_producer):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    init_db()
    os.makedirs(app.instance_path, exist_ok=True)
    Config(app, config_module="event_api.config")
    build_v1_routes(app, prefix="events")
    ExceptionHandling(app)
    DatabaseConnection(app)
    ServiceAccountAuth(app)

    with patch("event_api.endpoints.v1.event_view.KafkaProducer", return_value=kafka_producer):
        yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture
def database_ctx(flask_app):
    company = Company.create(name="ExampleCompany")
    org = Organization.create(name="ExampleOrganization", company=company)
    proj = Project.create(name="ExampleProject", active=True, organization=org)
    key = generate_key(allowed_services=[flask_app.config["SERVICE_NAME"]], project=proj).encoded_key
    yield DatabaseCtx(proj, company, org, key)
    DB.close()


@pytest.fixture
def service_account_key_headers(database_ctx):
    return {ServiceAccountAuth.header_name: database_ctx.service_key}


@pytest.fixture
def headers(service_account_key_headers):
    # Just a single source of headers
    return service_account_key_headers


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        yield client
