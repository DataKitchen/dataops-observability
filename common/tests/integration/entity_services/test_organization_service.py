import pytest

from common.entities import Company, Organization, Project
from common.entity_services import OrganizationService
from common.entity_services.helpers import ListRules, Page, SortOrder


@pytest.fixture(autouse=True)
def local_test_db(test_db):
    yield test_db


def _add_company_to_db() -> Company:
    return Company.create(name="Foo")


@pytest.mark.integration
def test_get_projects_with_rules():
    company = _add_company_to_db()
    org = Organization.create(name="O1", company=company)
    proj1 = Project.create(name="P1", organization=org)
    proj2 = Project.create(name="P2", organization=org)
    page = OrganizationService.get_projects_with_rules(org.id, ListRules())
    assert isinstance(page, Page)
    assert len(page.results) == 2
    assert page.total == 2
    assert page.results[0].id == proj1.id
    assert page.results[1].id == proj2.id


@pytest.mark.integration
def test_get_projects_with_rules_paginated():
    company = _add_company_to_db()
    org = Organization.create(name="O1", company=company)
    Project.create(name="P1", organization=org)
    proj2 = Project.create(name="P2", organization=org)
    page = OrganizationService.get_projects_with_rules(org.id, ListRules(page=2, count=1))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 2
    assert page.results[0].id == proj2.id


@pytest.mark.integration
def test_get_projects_with_rules_search():
    company = _add_company_to_db()
    org = Organization.create(name="O1", company=company)
    Project.create(name="P1", organization=org)
    proj2 = Project.create(name="Longish Name", organization=org)
    page = OrganizationService.get_projects_with_rules(org.id, ListRules(search="ish"))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 1
    assert page.results[0].id == proj2.id


@pytest.mark.integration
def test_get_projects_with_rules_paginated_sorted():
    company = _add_company_to_db()
    org = Organization.create(name="O1", company=company)
    proj1 = Project.create(name="P1", organization=org)
    Project.create(name="P2", organization=org)
    page = OrganizationService.get_projects_with_rules(org.id, ListRules(page=2, count=1, sort=SortOrder.DESC))
    assert isinstance(page, Page)
    assert len(page.results) == 1
    assert page.total == 2
    assert page.results[0].id == proj1.id
