from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest

from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.v1 import users as UserRoutes
from observability_api.schemas.user_schemas import UserSchema


@pytest.fixture
def user_service():
    svc = Mock()
    UserRoutes.UserService = svc
    yield svc


@pytest.fixture
def user_model():
    model = Mock()
    UserRoutes.User = model
    yield model


@pytest.fixture
def company_model():
    model = Mock()
    UserRoutes.Company = model
    yield model


@pytest.mark.unit
@patch("observability_api.schemas.user_schemas.UserSchema.dump", return_value=[])
def test_user_list_empty(_schema_dump_mock, client, user_service, user, user_admin_role):
    user_service.list_with_rules = Mock(return_value=Page(results=[], total=0))
    old_rules = UserRoutes.ListRules.from_params
    UserRoutes.ListRules.from_params = Mock(return_value=ListRules())
    response = client.get("/observability/v1/users")
    assert response.status_code == HTTPStatus.OK, response.json
    UserRoutes.ListRules.from_params.assert_called_once()
    user_service.list_with_rules.assert_called_once_with(
        UserRoutes.ListRules.from_params.return_value, company_id=None, name_filter=None
    )
    _schema_dump_mock.assert_called_once()
    UserRoutes.ListRules.from_params = old_rules


@pytest.mark.unit
def test_user_get_by_id_has_request_body(client, user_service, user_model, user):
    UserSchema.dump_with_params = Mock(return_value={})
    user_model.get_by_id = Mock()
    response = client.get(
        f"/observability/v1/users/{user.id}", headers={"Content-Type": "application/json"}, json={"foo": "bar"}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    user_model.get_by_id.assert_not_called()
    UserSchema.dump_with_params.assert_not_called()
