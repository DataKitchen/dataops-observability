import uuid
from http import HTTPStatus

import pytest

from common.entities import Organization


@pytest.mark.integration
def test_list_organizations(client, g_user, company, organization):
    organization2 = Organization.create(name="Bar", company=company)
    response = client.get(f"/observability/v1/companies/{company.id}/organizations")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 2
    assert data["entities"][1]["name"] in (organization.name, organization2.name)
    assert data["total"] == 2


@pytest.mark.integration
def test_list_organizations_pagination(client, g_user, company):
    Organization.create(name="Bar", company=company)
    response = client.get(f"/observability/v1/companies/{company.id}/organizations?page=2")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 0
    assert data["total"] == 1


@pytest.mark.integration
def test_list_organizations_company_forbidden(client, g_user_2, company):
    response = client.get(f"/observability/v1/companies/{company.id}/organizations")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_organizations_company_not_found(client, g_user):
    response = client.get(f"/observability/v1/companies/{uuid.uuid4()}/organizations")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_get_organization_by_id(client, g_user, organization):
    response = client.get(f"/observability/v1/organizations/{organization.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(organization.id)


@pytest.mark.integration
def test_get_organization_by_id_forbidden(client, g_user_2, organization):
    response = client.get(f"/observability/v1/organizations/{organization.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_organizations_by_id_not_found(client, g_user):
    response = client.get(f"/observability/v1/organizations/{uuid.uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
