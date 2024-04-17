import pytest

from common.entities import Company, Role, User, UserRole


@pytest.mark.integration
def test_user_has_role_on():
    company = Company.create(name="Foo")
    user = User.create(name="Not Max", email="bar", foreign_user_id="def", primary_company=company)
    role = Role.create(name="test-user-role")
    UserRole.create(user=user, role=role)
    assert user.has_role("test-user-role") is True
    assert user.has_role("this-role-no-existy") is False
