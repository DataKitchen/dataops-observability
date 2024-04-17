import os
import shutil
from dataclasses import dataclass

import pytest
from flask import Flask

from agent_api.config.defaults import API_PREFIX
from agent_api.routes import build_v1_routes
from common.api.flask_ext.authentication import ServiceAccountAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.health import Health
from common.auth.keys.service_key import generate_key
from common.entities import DB, Company, Organization, Project
from conf import init_db


@dataclass
class DatabaseCtx:
    project: Project
    company: Company
    organization: Organization
    service_key: str


@pytest.fixture(autouse=True)
def test_db():
    yield init_db()
    DB.close()


@pytest.fixture
def flask_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    build_v1_routes(app, prefix=API_PREFIX)
    Config(app, config_module="agent_api.config")
    app.config["DEBUG"] = True
    Health(app, prefix=API_PREFIX, readiness_callback=lambda: None)
    ServiceAccountAuth(app)

    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture
def database_ctx(flask_app):
    company = Company.create(name="ExampleCompany")
    org = Organization.create(name="ExampleOrganization", company=company)
    proj = Project.create(name="ExampleProject", active=True, organization=org)
    key = generate_key(allowed_services=[flask_app.config["SERVICE_NAME"]], project=proj).encoded_key
    yield DatabaseCtx(proj, company, org, key)


@pytest.fixture
def headers(database_ctx):
    # Just a single source of headers
    return {ServiceAccountAuth.header_name: database_ctx.service_key}


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client
