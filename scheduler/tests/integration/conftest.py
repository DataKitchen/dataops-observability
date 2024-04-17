import pytest

from common.entities import DB, Company, Organization, Pipeline, Project
from conf import init_db


@pytest.fixture(autouse=True)
def test_db():
    yield init_db()
    DB.close()


@pytest.fixture
def company():
    return Company.create(name="C1")


@pytest.fixture
def organization(company):
    return Organization.create(name="O1", company=company)


@pytest.fixture
def project(organization):
    return Project.create(name="P1", organization=organization, active=True)


@pytest.fixture
def pipeline(project):
    return Pipeline.create(key="Test Pipeline", project=project)
