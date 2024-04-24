import uuid
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest

from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.v1 import projects as ProjectsRoutes
from observability_api.endpoints.v1.projects import ProjectById, Projects


@pytest.fixture
def organization_model(organization):
    model = Mock()
    ProjectsRoutes.Organization = model
    yield model


@pytest.fixture
def project_model(organization):
    model = Mock()
    ProjectsRoutes.Project = model
    yield model


@pytest.fixture
def organization_service():
    svc = Mock()
    ProjectsRoutes.OrganizationService = svc
    yield svc


@pytest.fixture
def project_service():
    svc = Mock()
    ProjectsRoutes.ProjectService = svc
    yield svc


@pytest.fixture(autouse=True)
def mock_project_db(mock_db):
    old_db = ProjectsRoutes.DB
    ProjectsRoutes.DB = mock_db
    yield
    ProjectsRoutes.DB = old_db


@patch("observability_api.endpoints.v1.projects.ListRules.from_params", return_value=ListRules())
@patch("observability_api.endpoints.v1.projects.ProjectSchema.dump", return_value=[])
@pytest.mark.unit
def test_project_list_empty(_mock_dump, _mock_rules, client, organization_service, organization, organization_model):
    Projects.get_entity_or_fail = Mock()
    organization_service.get_projects_with_rules = Mock(return_value=Page(results=[], total=0))
    response = client.get(f"/observability/v1/organizations/{uuid.uuid4()}/projects")
    assert response.status_code == HTTPStatus.OK, response.json
    _mock_rules.assert_called_once()
    organization_service.get_projects_with_rules.assert_called_once()
    _mock_dump.assert_called_once()
    Projects.get_entity_or_fail.assert_called_once()


@pytest.mark.unit
@patch("observability_api.endpoints.v1.projects.ProjectSchema.dump", return_value={})
def test_project_get_by_id_has_request_body(mock_dump, client, organization_service, project_model, project):
    ProjectById.get_entity_or_fail = Mock()
    response = client.get(
        f"/observability/v1/projects/{project.id}", headers={"Content-Type": "application/json"}, json={"foo": "bar"}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    project_model.get_by_id.assert_not_called()
    mock_dump.assert_not_called()
    ProjectById.get_entity_or_fail.assert_not_called()
