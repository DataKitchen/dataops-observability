import pytest

from common.entities import AuthProvider, Company, Organization, User
from common.entity_services import CompanyService
from common.entity_services.helpers import ListRules, Page, SortOrder


@pytest.fixture(autouse=True)
def local_test_db(test_db):
    yield test_db


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
def test_get_organizations_with_rules():
    _, company = _add_company_to_db()
    org1 = Organization.create(name="O1", company=company)
    org2 = Organization.create(name="O2", company=company)
    page = CompanyService.get_organizations_with_rules(company.id, ListRules())
    assert isinstance(page, Page)
    assert len(page.results) == 2
    assert page.total == 2
    assert page.results[0].id == org1.id
    assert page.results[1].id == org2.id


@pytest.mark.integration
def test_get_organizations_with_rules_paginated():
    _, company = _add_company_to_db()
    Organization.create(name="O1", company=company)
    org2 = Organization.create(name="O2", company=company)
    page = CompanyService.get_organizations_with_rules(company.id, ListRules(page=2, count=1))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 2
    assert page.results[0].id == org2.id


@pytest.mark.integration
def test_get_organizations_with_rules_paginated_sorted():
    _, company = _add_company_to_db()
    org1 = Organization.create(name="O1", company=company)
    Organization.create(name="O2", company=company)
    page = CompanyService.get_organizations_with_rules(company.id, ListRules(page=2, count=1, sort=SortOrder.DESC))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 2
    assert page.results[0].id == org1.id


@pytest.mark.integration
def test_get_users_with_rules():
    _, company = _add_company_to_db()
    user1 = User.create(name="A", email="bar", primary_company=company, foreign_user_id="abc")
    user2 = User.create(name="B", email="bat", primary_company=company, foreign_user_id="abc2")
    page = CompanyService.get_users_with_rules(company.id, ListRules())
    assert isinstance(page, Page)
    assert len(page.results) == 2
    assert page.total == 2
    assert page.results[0].id == user1.id
    assert page.results[1].id == user2.id


@pytest.mark.integration
def test_get_users_with_rules_paginated():
    _, company = _add_company_to_db()
    User.create(name="A", email="bar", primary_company=company, foreign_user_id="abc")
    user2 = User.create(name="B", email="bat", primary_company=company, foreign_user_id="abc2")
    page = CompanyService.get_users_with_rules(company.id, ListRules(page=2, count=1))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 2
    assert page.results[0].id == user2.id


@pytest.mark.integration
def test_get_users_with_rules_paginated_sorted():
    _, company = _add_company_to_db()
    user1 = User.create(name="A", email="bar", primary_company=company, foreign_user_id="abc")
    User.create(name="B", email="bat", primary_company=company, foreign_user_id="abc2")
    page = CompanyService.get_users_with_rules(company.id, ListRules(page=2, count=1, sort=SortOrder.DESC))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 2
    assert page.results[0].id == user1.id
