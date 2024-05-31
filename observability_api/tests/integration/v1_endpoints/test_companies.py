from http import HTTPStatus

import pytest


@pytest.mark.integration
def test_get_company_by_id(client, company, g_user):
    response = client.get(f"/observability/v1/companies/{company.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(company.id)


@pytest.mark.integration
def test_get_company_by_id_with_body(client, company, g_user):
    response = client.get(f"/observability/v1/companies/{company.id}", json={"foo": "bar"})
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_get_company_by_id_forbidden(client, company, g_user_2):
    response = client.get(f"/observability/v1/companies/{company.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_company_by_id_not_found(client, g_user_2_admin):
    response = client.get("/observability/v1/companies/999")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
