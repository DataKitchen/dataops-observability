import pytest
from peewee import IntegrityError

from common.entities import Action, ActionImpl, Company


@pytest.mark.integration
def test_action_no_dupliate_action_name(company):
    Action.create(name="test action", action_impl=ActionImpl.SEND_EMAIL, company=company)
    with pytest.raises(IntegrityError):
        Action.create(name="test action", company=company)


@pytest.mark.integration
def test_action_same_name_different_company(company):
    company2 = Company.create(name="fake company2")
    Action.create(name="test action", action_impl=ActionImpl.SEND_EMAIL, company=company)
    Action.create(name="test action", action_impl=ActionImpl.SEND_EMAIL, company=company2)


@pytest.mark.integration
def test_action_defaults(company):
    action = Action.create(name="test action", action_impl=ActionImpl.SEND_EMAIL, company=company)
    assert action.action_args == {}
