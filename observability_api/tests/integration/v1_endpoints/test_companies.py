from http import HTTPStatus

import pytest

from common.entities import AuthProvider, Company


def _add_company_to_db(
    *,
    client_id: str = "foo",
    client_secret: str = "bar",
    discovery_doc_url: str = "https://baz.com/discovery",
    domain: str = "baz.com",
    name: str = "Foo",
):
    company = Company.create(name=name)
    provider: AuthProvider = AuthProvider.create(
        client_id=client_id,
        client_secret=client_secret,
        discovery_doc_url=discovery_doc_url,
        domain=domain,
        company=company,
    )
    return provider, company


@pytest.mark.integration
def test_list_companies(client, g_user_2_admin):
    _, foo_company = _add_company_to_db()
    _, fizz_company = _add_company_to_db(client_id="fizz", client_secret="buzz", domain="boom.com", name="Fizz")
    response = client.get("/observability/v1/companies")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 4
    assert data["entities"][1]["name"] in (
        foo_company.name,
        fizz_company.name,
        g_user_2_admin.user.primary_company.name,
    )
    assert data["total"] == 4


@pytest.mark.integration
def test_list_companies_pagination(client, g_user_2_admin):
    _, foo_company = _add_company_to_db()
    _, fizz_company = _add_company_to_db(client_id="fizz", client_secret="buzz", domain="boom.com", name="Fizz")
    response = client.get("/observability/v1/companies?page=2")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 0
    assert data["total"] == 4


@pytest.mark.integration
@pytest.mark.parametrize("auth_method", ["g_user", "g_project"], ids=["non-admin user", "SA key"])
def test_list_companies_forbidden(client, auth_method, request):
    _ = request.getfixturevalue(auth_method)
    response = client.get("/observability/v1/companies")

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_company_by_id(client, company, g_user):
    response = client.get(f"/observability/v1/companies/{company.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(company.id)


@pytest.mark.integration
def test_get_company_by_id_forbidden(client, g_user_2):
    provider, company = _add_company_to_db()
    response = client.get(f"/observability/v1/companies/{company.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_company_by_id_not_found(client, g_user_2_admin):
    response = client.get("/observability/v1/companies/999")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
