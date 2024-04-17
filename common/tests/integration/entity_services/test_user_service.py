import pytest

from common.entities import AuthProvider, Company, User
from common.entity_services import UserService
from common.entity_services.helpers import ListRules


@pytest.fixture(autouse=True)
def local_test_db(test_db):
    yield test_db


@pytest.mark.integration
def test_list_with_rules():
    company = Company.create(name="Foo")
    user = User.create(name="Max", email="foo", foreign_user_id="abc", primary_company=company)
    page = UserService.list_with_rules(ListRules())
    assert len(page.results) == 1
    assert page.results[0].name == user.name
    assert page.total == 1


@pytest.mark.integration
def test_list_with_rules_filter_company():
    company = Company.create(name="Foo")
    provider = AuthProvider.create(
        client_id="foo", client_secret="bar", domain="baz.com", company=company, discovery_doc_url="foo"
    )
    other_company = Company.create(name="Bar", subdomain="baz", auth_provider_id=provider.id)
    user = User.create(name="Max", email="foo", foreign_user_id="abc", primary_company=company)
    User.create(name="Not Max", email="bar", foreign_user_id="def", primary_company=other_company)
    page = UserService.list_with_rules(ListRules(), company_id=company.id)
    assert len(page.results) == 1
    assert page.results[0].name == user.name
    assert page.total == 1


@pytest.mark.integration
@pytest.mark.parametrize("name_filter", ("not", "Not", "NOT"), ids=("lower", "capital", "all_caps"))
def test_list_with_rules_filter_user_name(name_filter):
    company = Company.create(name="Foo")
    provider = AuthProvider.create(
        client_id="foo", client_secret="bar", domain="baz.com", company=company, discovery_doc_url="foo"
    )
    other_company = Company.create(name="Bar", subdomain="baz", auth_provider_id=provider.id)
    User.create(name="Max", email="foo", foreign_user_id="abc", primary_company=company)
    user = User.create(name="Not Max", email="bar", foreign_user_id="def", primary_company=other_company)
    page = UserService.list_with_rules(ListRules(), name_filter=name_filter)
    assert len(page.results) == 1
    assert page.results[0].name == user.name
    assert page.total == 1
