from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest

from common.entity_services.helpers import ListRules, Page


@pytest.fixture
def company_model():
    with patch("observability_api.endpoints.v1.companies.Company") as company_model:
        yield company_model


@pytest.fixture
def organization_model():
    with patch("observability_api.endpoints.v1.companies.Organization") as org_model:
        yield org_model


@pytest.fixture
def project_model():
    with patch("observability_api.endpoints.v1.companies.Project") as proj_model:
        yield proj_model


@pytest.fixture
def company_service():
    with patch("observability_api.endpoints.v1.companies.CompanyService") as company_service:
        yield company_service


@patch("observability_api.endpoints.v1.companies.CompanySchema.dump", return_value=[])
@patch(
    "observability_api.endpoints.v1.companies.ListRules.from_params",
    return_value=ListRules(),
)
@pytest.mark.unit
def test_company_list_forbidden(_mock_1, _mock_2, client, company_service, company):
    company_service.list_with_rules = Mock(return_value=Page(results=[company], total=1))
    response = client.get("/observability/v1/companies")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@patch("observability_api.endpoints.v1.companies.CompanySchema.dump", return_value={})
@pytest.mark.unit
def test_company_get_by_id_has_request_body(_mock_schema_dump, client, company_model, company):
    company_model.get_by_id = Mock()
    response = client.get(
        f"/observability/v1/companies/{company.id}", headers={"Content-Type": "application/json"}, json={"foo": "bar"}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    company_model.get_by_id.assert_not_called()
    _mock_schema_dump.assert_not_called()
