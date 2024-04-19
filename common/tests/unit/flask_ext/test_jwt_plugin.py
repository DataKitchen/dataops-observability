import json
from base64 import b64decode, b64encode
from binascii import Error as B64DecodeError
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from jwt import encode
from jwt.exceptions import InvalidSignatureError

from common.api.flask_ext.authentication.jwt_plugin import JWTAuth, get_token_expiration
from common.entities import User

TOKEN_DATA = {
    "nickname": "testuser+dk",
    "name": "testuser@domain.com",
    "picture": "https://noreply/fake.png",
    "updated_at": "2021-12-02T21:16:20.356Z",
    "email": "testuser@domain.com",
    "email_verified": True,
    "iss": "https://example.auth0.com/",
    "sub": "auth0|5e541654edafc00d7c80fc62",
    "aud": "2tL5WT2vrvaeGjaHOeCuDH8qCXJcttwU",
    "iat": 1638479780,
    "exp": 1638487580,
}
JWT_KEY = "42420b68db2ef424242b6d42c3ea42dc2f42be6424242cd9fbc3"


@pytest.fixture
def get_domain_mock():
    with patch("common.api.flask_ext.authentication.jwt_plugin.get_domain", return_value="fake.domain") as mock:
        yield mock


@pytest.fixture(autouse=True)
def install_plugin():
    app = Mock()
    app.secret_key = JWT_KEY
    app.config = {"DEFAULT_JWT_EXPIRATION_SECONDS": 100}
    JWTAuth(app)


@pytest.fixture
def expired_token():
    return encode(TOKEN_DATA, key=JWT_KEY)


@pytest.fixture
def current_token():
    data = TOKEN_DATA.copy()
    dt = datetime.now(timezone.utc) + timedelta(days=2)
    data["exp"] = int(dt.replace(microsecond=0).timestamp())
    return encode(data, key=JWT_KEY)


@pytest.fixture
def user():
    return User(id=uuid4(), primary_company=uuid4())


@pytest.mark.unit
@pytest.mark.parametrize(
    ("ts_value", "dt_value"),
    [
        (40, datetime(1970, 1, 1, 0, 0, 40, tzinfo=timezone.utc)),
        (435474000, datetime(1983, 10, 20, 5, 0, tzinfo=timezone.utc)),
    ],
)
def test_get_expiration_int(ts_value, dt_value):
    assert get_token_expiration({"exp": ts_value}) == dt_value
    assert get_token_expiration({"exp": float(ts_value)}) == dt_value


@pytest.mark.unit
@pytest.mark.parametrize(
    ("value", "exception_class"),
    [
        (None, ValueError),
        ("4", ValueError),
        ("J", ValueError),
    ],
)
def test_get_expiration_bad(value, exception_class):
    with pytest.raises(exception_class):
        get_token_expiration({"exp": value})


@pytest.mark.unit
def test_encode_and_decode_token():
    try:
        token = JWTAuth.encode_token(TOKEN_DATA)
    except Exception as e:
        raise AssertionError("Encoding token should not raise an exception") from e
    claims = JWTAuth.decode_token(token)
    assert claims == TOKEN_DATA


@pytest.mark.unit
def test_bearer_tampering():
    t = JWTAuth.encode_token(TOKEN_DATA)
    jwt_info, data, signature = t.split(".")
    while True:
        try:
            decoded = b64decode(data)
        except B64DecodeError:
            data += "="  # Add padding until valid base64
        else:
            break

    decoded_str = decoded.decode("utf-8")
    payload_data = json.loads(decoded_str)
    payload_data["email"] = "testuser@domain.com"  # Oh no! Token tampering!
    dumped = json.dumps(payload_data).encode("utf-8")
    encoded = b64encode(dumped).decode("utf-8").rstrip("=")  # Remove padding
    tampered_token = f"{jwt_info}.{encoded}.{signature}"
    with pytest.raises(InvalidSignatureError):
        JWTAuth.decode_token(tampered_token)
