__all__ = ["JWTAuth"]
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, cast

from flask import current_app, g, request
from jwt import decode, encode
from peewee import DoesNotExist
from werkzeug.exceptions import Unauthorized

from common.entities import User
from common.typing import JWT_CLAIMS

from .common import BaseAuthPlugin, get_domain, validate_authentication

LOG = logging.getLogger(__name__)


def get_token_expiration(claims: JWT_CLAIMS) -> datetime:
    """Returns the JWT expiration as a datetime object."""
    try:
        exp_timestamp = claims["exp"]
    except KeyError:
        raise ValueError("Token claims missing 'exp' key")
    try:
        return datetime.fromtimestamp(cast(float | int, exp_timestamp), tz=timezone.utc)
    except Exception:
        raise ValueError(f"Unable to parse expiration from '{claims['exp']}'")


class JWTAuth(BaseAuthPlugin):
    header_name = "Authorization"
    header_prefix = "Bearer"

    default_jwt_options: dict[str, object] = {"verify_signature": True, "verify_aud": False, "verify_exp": False}
    """Default options for decoding JWT values."""

    default_jwt_expiration: timedelta = NotImplemented
    """Default JWT expiration."""

    jwt_algorithm = "HS256"

    logout_callbacks: dict[str, Callable] = {}
    """Callback functions to be called when the user logs out."""

    secret_key: str = NotImplemented
    """
    Secret key utilized to encode/decode the JTW tokens.
    It is automatically set after flask's namesake setting upon initialization.
    """

    @classmethod
    def pre_request_auth(cls) -> None:
        if request.endpoint in current_app.config.get("AUTHENTICATION_EXCLUDED_ROUTES", ()):
            return None
        jwt_token = cls.get_header_data()
        if not jwt_token:
            return None

        try:
            claims = cls.decode_token(jwt_token)
        except Exception as e:
            raise Unauthorized("Invalid authentication token") from e

        if get_token_expiration(claims) < datetime.now(timezone.utc):
            LOG.error("JWT token expired")
            raise Unauthorized("Invalid authentication token")

        if (claims_domain := claims.get("domain", "")) != (current_domain := get_domain()):
            LOG.error("Attempted to use token for `%s` on `%s`", claims_domain, current_domain)
            raise Unauthorized("Invalid authentication token")

        try:
            user = User.select().where(User.id == claims["user_id"], User.primary_company == claims["company_id"]).get()
        except DoesNotExist:
            LOG.error("User in claims does not exist")
            raise Unauthorized("Invalid authentication token")
        except KeyError:
            LOG.error("Mandatory claims missing. Impossible to authorize user")
            raise Unauthorized("Invalid authentication token")

        g.user = user
        g.claims = claims

    @classmethod
    def encode_token(cls, token_dict: JWT_CLAIMS) -> str:
        return encode(token_dict, key=cls.secret_key, algorithm=cls.jwt_algorithm)

    @classmethod
    def decode_token(cls, token: str) -> JWT_CLAIMS:
        decoded_token: JWT_CLAIMS = decode(
            token, key=cls.secret_key, options=cls.default_jwt_options, algorithms=[cls.jwt_algorithm]
        )
        return decoded_token

    @classmethod
    def log_user_in(cls, user: User, logout_callback: Optional[str] = None, claims: Optional[JWT_CLAIMS] = None) -> str:
        claims = claims or {}

        if logout_callback:
            if logout_callback in cls.logout_callbacks:
                claims["logout_callback"] = logout_callback
            else:
                raise ValueError(f"Logout callback '{logout_callback}' is not registered.")

        if "exp" not in claims:
            claims["exp"] = (datetime.now(timezone.utc) + cls.default_jwt_expiration).timestamp()

        claims["user_id"] = str(user.id)
        claims["company_id"] = str(user.primary_company_id)
        claims["domain"] = get_domain()

        g.user = user
        g.claims = claims

        return cls.encode_token(claims)

    @classmethod
    def log_user_out(cls) -> None:
        user = getattr(g, "user", None)
        if not user:
            LOG.warning("Could not end user's session because user is not authenticated")
            return

        claims = getattr(g, "claims", {})
        if logout_callback_key := claims.get("logout_callback"):
            try:
                logout_callback = cls.logout_callbacks[logout_callback_key]
            except KeyError as e:
                LOG.error("Logout callback not found: %s", e)
            else:
                try:
                    logout_callback()
                except Exception:
                    LOG.exception("Error executing logout callback")

    @classmethod
    def register_logout_callback(cls, key: str) -> Callable:
        if key in cls.logout_callbacks:
            raise ValueError("The provided key is already taken")

        def register_callback(callback: Callable) -> Callable:
            cls.logout_callbacks[key] = callback
            return callback

        return register_callback

    def init_app(self) -> None:
        if self.app is not None:
            self.add_before_request_func(JWTAuth.pre_request_auth)
            self.add_or_move_before_request_func(validate_authentication)
            if self.app.secret_key:
                self.__class__.secret_key = self.app.secret_key
                self.__class__.default_jwt_expiration = timedelta(
                    seconds=self.app.config["DEFAULT_JWT_EXPIRATION_SECONDS"]
                )
            else:
                raise RuntimeError("Flask's SECRET_KEY must be set to enable JWT")
