import base64
from http import HTTPStatus

import pytest

from testlib.fixtures.entities import *


@pytest.fixture
def basic_credentials(basic_auth_user):
    cred_bytes = f"{basic_auth_user.username}:{BASIC_AUTH_USER_PASSWORD}".encode()
    return base64.b64encode(cred_bytes).decode()


@pytest.mark.integration
def test_login_ok(jwt_client, basic_auth_user, basic_credentials):
    auth = {"Authorization": f"Basic {basic_credentials}", "Origin": "https://fakedomain.fake"}
    response = jwt_client.get("/observability/v1/auth/basic", headers=auth)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.integration
def test_login_inactive_user_403(jwt_client, basic_auth_user, basic_credentials):
    basic_auth_user.active = False
    basic_auth_user.save()
    auth = {"Authorization": f"Basic {basic_credentials}"}
    response = jwt_client.get("/observability/v1/auth/basic", headers=auth)
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.integration
def test_login_incorrect_password(jwt_client, basic_auth_user):
    credential = base64.b64encode((f"{basic_auth_user.username}:invalid").encode()).decode()
    auth = {"Authorization": "Basic " + credential}
    response = jwt_client.get("/observability/v1/auth/basic", headers=auth)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_login_user_not_found(jwt_client, basic_auth_user):
    credential = base64.b64encode((f"dne_user:{BASIC_AUTH_USER_PASSWORD}").encode()).decode()
    auth = {"Authorization": "Basic " + credential}
    response = jwt_client.get("/observability/v1/auth/basic", headers=auth)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_login_missing_header(jwt_client, basic_auth_user):
    response = jwt_client.get("/observability/v1/auth/basic", headers={})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_login_bad_header(jwt_client, basic_auth_user):
    auth = {"Authorization": "Basic notb64string"}
    response = jwt_client.get("/observability/v1/auth/basic", headers=auth)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.integration
def test_basic_auth_disabled_when_sso_enabled(jwt_client, basic_auth_user, basic_credentials, auth_provider):
    auth = {"Authorization": f"Basic {basic_credentials}", "Origin": f"http://{auth_provider.domain}"}
    response = jwt_client.get("/observability/v1/auth/basic", headers=auth)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
