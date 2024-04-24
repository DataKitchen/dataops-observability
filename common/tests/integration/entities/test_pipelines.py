import pytest
from peewee import IntegrityError

from common.entities import Company, Organization, Pipeline, Project


@pytest.fixture
def company():
    c = Company.create(name="Fake Company")
    yield c


@pytest.fixture
def organization(company):
    org = Organization.create(name="Fake Organization", company=company)
    yield org


@pytest.fixture
def project(organization):
    prog = Project.create(name="Fake Project", organization=organization)
    yield prog


@pytest.fixture
def project_2(organization):
    project = Project.create(name="Fake Project 2", organization=organization)
    yield project


@pytest.mark.integration
def test_add_pipeline_no_duplicate_pipeline_key(project):
    """Creating duplicate pipline keys in the same project yields an IntegrityError."""
    Pipeline.create(key="Fake Pipeline", project=project)
    with pytest.raises(IntegrityError):
        Pipeline.create(key="Fake Pipeline", project=project)


@pytest.mark.integration
def test_add_pipeline_duplicate_name(project, project_2):
    """Duplicated names are allowed in different projects."""
    Pipeline.create(key="Fake Pipeline", project=project)
    try:
        Pipeline.create(key="Fake Pipeline", project=project_2)
    except IntegrityError:
        raise AssertionError("Adding duplicate Pipeline name to a different project should not fail integrity check")


@pytest.mark.integration
def test_pipeline_display_name(project):
    pipe = Pipeline.create(key="mykey", name="some name", project=project)
    assert "some name" == pipe.display_name


@pytest.mark.integration
def test_pipeline_display_name_fallback(project):
    pipe = Pipeline.create(key="mykey", project=project)
    assert "mykey" == pipe.display_name
