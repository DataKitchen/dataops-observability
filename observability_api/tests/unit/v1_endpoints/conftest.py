import os
import shutil
import uuid
from http.client import HTTPException
from unittest.mock import Mock, PropertyMock, patch

import pytest
from flask import Flask, g

from common.api.flask_ext.exception_handling import ExceptionHandling
from common.entities import DB, AuthProvider, Company, Organization, Project, Service, ServiceAccountKey, User
from observability_api.config.defaults import API_PREFIX
from observability_api.routes import build_v1_routes


@pytest.fixture
def datakitchen_company():
    """Separate fixture for this since there's special behavior for this Company"""
    yield Company(id=uuid.uuid4(), name="DataKitchen")


@pytest.fixture
def test_user(datakitchen_company):
    yield User(id=uuid.uuid4(), name="Test User", primary_company=datakitchen_company)


@pytest.fixture
def flask_app(test_user):
    def mock_auth(*_) -> None:
        g.user = test_user

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(PROPAGATE_EXCEPTIONS=True)
    os.makedirs(app.instance_path, exist_ok=True)
    build_v1_routes(app, prefix=API_PREFIX)
    # We don't need to register the other handler because it's only used for catching unexpected errors.
    # Unit tests should never have "unexpected" errors.
    app.register_error_handler(HTTPException, ExceptionHandling.handle_http_errors)
    app.before_request(mock_auth)
    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_db():
    class MockDB(Mock):
        """Mock PeeWee Database instance, provides all things needed for test (faster than MagicMock)"""

        quote = '""'

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return

    mock_database_object = MockDB()
    mock_database_object.atomic = Mock(return_value=MockDB())
    DB.initialize(mock_database_object)
    yield DB
    DB.obj = None


@pytest.fixture(autouse=True)
def default_user_roles():
    with patch("common.api.base_view.BaseView.user_roles", PropertyMock(return_value=[])) as roles_mock:
        yield roles_mock


@pytest.fixture
def user_admin_role(default_user_roles):
    with patch.object(default_user_roles, "return_value", ["ADMIN"]):
        yield default_user_roles


@pytest.fixture
def company():
    yield Company(id=uuid.uuid4(), name="UnitTestCompany")


@pytest.fixture
def auth_provider(company):
    yield AuthProvider(
        id=uuid.uuid4(),
        client_id="test_client_id",
        client_secret="test_client_secret",
        domain="test_domain",
        company=company,
        discovery_doc_url="https://foo.bar/discovery",
    )


@pytest.fixture
def organization(company):
    yield Organization(id=uuid.uuid4(), name="UnitTestOrg", company=company)


@pytest.fixture
def project(organization):
    yield Project(id=uuid.uuid4(), name="UnitTestProject", organization=organization)


@pytest.fixture
def user(company):
    yield User(
        id=uuid.uuid4(),
        name="DKUser",
        email="user@dk.com",
        foreign_user_id="dkuser",
        primary_company=company,
    )


@pytest.fixture
def sa_key(project):
    yield ServiceAccountKey(id=uuid.uuid4(), allowed_services=Service.EVENTS_API.value, project=project)
