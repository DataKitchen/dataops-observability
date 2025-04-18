__all__ = ["CORS"]
from conf import settings
from http import HTTPStatus
from fnmatch import fnmatch
from typing import Optional
from urllib.parse import urlparse

from flask import Flask, Response, make_response, request
from werkzeug.exceptions import NotFound

from common.api.flask_ext.base_extension import BaseExtension

CORS_HEADERS: dict[str, str] = {
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers
    "Access-Control-Allow-Headers": "Accept, Content-Type, Origin, Host, Authorization, X-Forwarded-For",
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers
    # Add this only if we want to expose custom response headers
    # "Access-Control-Expose-Headers": "*",
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Credentials
    "Access-Control-Allow-Credentials": "true",
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age
    "Access-Control-Max-Age": "86400",
}


class CORS(BaseExtension):
    def __init__(self, app: Optional[Flask] = None, allowed_methods: Optional[list[str]] = None):
        allowed_methods = allowed_methods or []
        self.allowed_methods = ", ".join(allowed_methods + ["OPTIONS"]).upper()
        super().__init__(app)

    @staticmethod
    def make_preflight_response() -> Optional[Response]:
        if request.method == "OPTIONS":
            # When request.endpoint isn't populated it means that the URL didn't match any registered view. For this
            # case we abort and issue a 404
            if not request.endpoint:
                raise NotFound()
            response = make_response("", HTTPStatus.NO_CONTENT)
            return response
        else:
            return None

    def set_cors_headers(self, response: Response) -> Response:
        if response.headers is not None and (origin := request.headers.get("Origin")) is not None:
            try:
                netloc = urlparse(origin).netloc
                if any([fnmatch(netloc, pattern) for pattern in settings.CORS_DOMAINS]):
                    response.headers.update(CORS_HEADERS)
                    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Vary"] = "Origin"
                    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Methods
                    response.headers["Access-Control-Allow-Methods"] = self.allowed_methods
            except Exception:
                pass
        return response

    def init_app(self) -> None:
        self.add_before_request_func(CORS.make_preflight_response)
        self.add_after_request_func(self.set_cors_headers)
