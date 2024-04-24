from http import HTTPStatus
from uuid import uuid4

import pytest

from common.entities import Company, User


def _add_user_to_db(
    *,
    name: str = "foo",
    email: str = "bar@baz.com",
    user_id: str = "bat",
    company_name: str = "foo",
):
    try:
        company = Company.create(name=company_name)
        user = User.create(name=name, email=email, foreign_user_id=user_id, primary_company=company)
    except Exception as e:
        raise AssertionError("Error attempting to create test provider/company") from e
    return user


@pytest.mark.integration
def test_list_users(client, g_user_2_admin):
    user = _add_user_to_db()
    _add_user_to_db(name="fizz", email="buzz", user_id="Fizz", company_name="bar")
    response = client.get("/observability/v1/users")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 4
    assert user.name in (u["name"] for u in data["entities"])
    assert data["total"] == 4


@pytest.mark.integration
def test_list_users_pagination(client, g_user_2_admin):
    _add_user_to_db()
    _add_user_to_db(name="fizz", email="buzz", user_id="Fizz", company_name="bar")
    response = client.get("/observability/v1/users?page=2")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert len(data["entities"]) == 0

    assert data["total"] == 4


@pytest.mark.integration
def test_list_users_forbidden(client, g_user):
    response = client.get("/observability/v1/users")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_user_by_id(client, user, g_user_2_admin):
    response = client.get(f"/observability/v1/users/{user.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(user.id)


@pytest.mark.integration
def test_get_user_by_id_same_user(client, user, g_user):
    response = client.get(f"/observability/v1/users/{user.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(user.id)


@pytest.mark.integration
def test_get_user_by_id_forbidden(client, g_user):
    user = _add_user_to_db(email="some_other@user.com")
    response = client.get(f"/observability/v1/users/{user.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_user_by_id_not_found(client, user, g_user_2_admin):
    response = client.get(f"/observability/v1/users/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json
