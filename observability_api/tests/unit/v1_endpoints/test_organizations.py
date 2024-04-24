import uuid
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest

from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.v1 import organizations as OrganizationRoutes


@pytest.fixture
def company_model(company):
    model = Mock()
    OrganizationRoutes.Company = model
    yield model


@pytest.fixture
def organization_model(organization):
    model = Mock()
    OrganizationRoutes.Organization = model
    yield model


@pytest.fixture
def project_model(project):
    model = Mock()
    OrganizationRoutes.Project = model
    yield model


@pytest.fixture
def company_service():
    svc = Mock()
    OrganizationRoutes.CompanyService = svc
    yield svc


@pytest.fixture
def organization_service():
    svc = Mock()
    OrganizationRoutes.OrganizationService = svc
    yield svc


@pytest.fixture(autouse=True)
def mock_organization_db(mock_db):
    old_db = OrganizationRoutes.DB
    OrganizationRoutes.DB = mock_db
    yield
    OrganizationRoutes.DB = old_db


@patch("observability_api.endpoints.v1.organizations.ListRules.from_params", return_value=ListRules())
@patch("observability_api.endpoints.v1.organizations.OrganizationSchema.dump", return_value=[])
@pytest.mark.unit
def test_organization_list_empty(_mock_dump, _mock_rules, client, company_service, organization, company_model):
    OrganizationRoutes.Organizations.get_entity_or_fail = Mock(return_value=organization)
    company_model.get_by_id = Mock()
    company_service.get_organizations_with_rules = Mock(return_value=Page(results=[], total=0))
    response = client.get(f"/observability/v1/companies/{uuid.uuid4()}/organizations")
    assert response.status_code == HTTPStatus.OK, response.json
    _mock_rules.assert_called_once()
    company_service.get_organizations_with_rules.assert_called_once()
    _mock_dump.assert_called_once()
    OrganizationRoutes.Organizations.get_entity_or_fail.assert_called_once()


@patch("observability_api.endpoints.v1.organizations.OrganizationSchema.dump", return_value={})
@pytest.mark.unit
def test_organization_get_by_id_has_request_body(_mock_dump, client, organization_service, organization):
    OrganizationRoutes.OrganizationById.get_entity_or_fail = Mock(return_value=organization)
    response = client.get(
        f"/observability/v1/organizations/{organization.id}",
        headers={"Content-Type": "application/json"},
        json={"foo": "bar"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    OrganizationRoutes.OrganizationById.get_entity_or_fail.assert_not_called()
    _mock_dump.assert_not_called()
