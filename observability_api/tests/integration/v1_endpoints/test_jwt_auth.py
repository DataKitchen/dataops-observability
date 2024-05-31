from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from unittest.mock import patch
from uuid import uuid4

import pytest
from flask import g

from common.api.flask_ext.authentication import JWTAuth
from common.api.flask_ext.authentication.jwt_plugin import get_token_expiration
from common.constants import ADMIN_ROLE
from common.entities import Company, Role, User, UserRole


@pytest.fixture
def jwt_flask_app(flask_app):
    with (
        patch("common.api.flask_ext.authentication.common.get_domain", return_value="fakedomain.fake"),
        patch.dict(flask_app.config, {"DEFAULT_JWT_EXPIRATION_SECONDS": 20}),
    ):
        JWTAuth(flask_app)
        yield flask_app


@pytest.fixture
def jwt_client(jwt_flask_app):
    with jwt_flask_app.test_client() as client:
        with jwt_flask_app.app_context():
            yield client


@pytest.fixture
def admin_role(jwt_client) -> Role:
    role, _ = Role.get_or_create(name=ADMIN_ROLE)
    yield role


@pytest.fixture
def company_datakitchen(jwt_client) -> Company:
    company, _ = Company.get_or_create(name="DataKitchen")
    yield company


@pytest.fixture
def company_other(jwt_client) -> Company:
    company, _ = Company.get_or_create(name="Other")
    yield company


@pytest.fixture
def token_user(company_datakitchen, admin_role):
    user, _ = User.get_or_create(name="fakeuser+dk", primary_company=company_datakitchen, email="some@e.mail")
    UserRole.get_or_create(user=user, role=admin_role)
    yield user


@pytest.fixture
def valid_token(token_user):
    data = {
        "user_id": str(token_user.id),
        "company_id": str(token_user.primary_company_id),
        "domain": "fakedomain.fake",
    }
    dt = datetime.now(timezone.utc) + timedelta(days=2)
    data["exp"] = int(dt.replace(microsecond=0).timestamp())
    return JWTAuth.encode_token(data)


@pytest.fixture
def invalid_token_bad_user(token_user):
    data = {"user_id": str(uuid4()), "company_id": str(token_user.primary_company_id)}
    dt = datetime.now(timezone.utc) + timedelta(days=2)
    data["exp"] = int(dt.replace(microsecond=0).timestamp())
    return JWTAuth.encode_token(data)


@pytest.fixture
def g_user(jwt_flask_app, token_user):
    @jwt_flask_app.before_request
    def set_user():
        g.user = token_user

    return token_user


@pytest.mark.integration
def test_jwt_logout(jwt_client, valid_token, token_user):
    response = jwt_client.get(
        "/observability/v1/auth/logout",
        headers={"Authorization": f"Bearer {valid_token}", "Origin": "https://fakedomain.fake"},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json


@pytest.mark.integration
def test_jwt_invalid_user(jwt_client, token_user, invalid_token_bad_user, company):
    # Hit any endpoint that would normally need authorization and make sure that it raises an UNAUTHORIZED error
    response = jwt_client.get(
        f"/observability/v1/companies/{company.id}", headers={"Authorization": f"Bearer {invalid_token_bad_user}"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED, response.json


@pytest.mark.integration
def test_jwt_invalid_domain(jwt_client, token_user, valid_token, company):
    # Hit any endpoint that would normally need authorization and make sure that it raises an UNAUTHORIZED error
    response = jwt_client.get(
        f"/observability/v1/companies/{company.id}",
        headers={"Authorization": f"Bearer {valid_token}", "Origin": "https://wrongdomain.fake"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED, response.json


@pytest.mark.integration
def test_jwt_valid_user(jwt_client, token_user, valid_token, company):
    # Hit any endpoint that would normally need authorization and make sure that returns okay
    response = jwt_client.get(
        f"/observability/v1/companies/{company.id}",
        headers={"Authorization": f"Bearer {valid_token}", "Origin": "https://fakedomain.fake"},
    )
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
def test_jwt_login_user(jwt_client, token_user, company):
    with patch("common.api.flask_ext.authentication.jwt_plugin.get_domain", return_value="fakedomain.fake"):
        token = JWTAuth.log_user_in(token_user)

    # Hit any endpoint that would normally need authorization and make sure that returns okay
    response = jwt_client.get(
        f"/observability/v1/companies/{company.id}",
        headers={"Authorization": f"Bearer {token}", "Origin": "https://fakedomain.fake"},
    )
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
def test_jwt_token_expiration(jwt_client, token_user):
    with patch("common.api.flask_ext.authentication.jwt_plugin.get_domain", return_value="fakedomain.fake"):
        token = JWTAuth.log_user_in(token_user)

    claims = JWTAuth.decode_token(token)
    assert get_token_expiration(claims) < datetime.now(timezone.utc) + timedelta(seconds=20)


@pytest.mark.integration
def test_jwt_token_expiration_explicit(jwt_client, token_user):
    with patch("common.api.flask_ext.authentication.jwt_plugin.get_domain", return_value="fakedomain.fake"):
        token = JWTAuth.log_user_in(
            token_user, claims={"exp": (datetime.now(timezone.utc) + timedelta(seconds=10)).timestamp()}
        )

    claims = JWTAuth.decode_token(token)
    assert get_token_expiration(claims) < datetime.now(timezone.utc) + timedelta(seconds=10)
