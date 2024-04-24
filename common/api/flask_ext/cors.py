__all__ = ["CORS"]
from http import HTTPStatus
from typing import Optional

from flask import Flask, Response, make_response, request
from werkzeug.exceptions import NotFound

from common.api.flask_ext.base_extension import BaseExtension

# TODO: See PD-286 -- at some point we should not just use wildcards and actually settle on a strategy of indicating
# which domains to accept cross-origin-resource-sharing from.
CORS_HEADERS: dict[str, str] = {
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin
    "Access-Control-Allow-Origin": "*",
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers
    "Access-Control-Allow-Headers": "*",
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Methods
    "Access-Control-Allow-Methods": "*",
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers
    "Access-Control-Expose-Headers": "*",
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

    @staticmethod
    def set_cors_headers(response: Response) -> Response:
        if response.headers is not None:
            response.headers.update(CORS_HEADERS)
            return response

    def init_app(self) -> None:
        self.add_before_request_func(CORS.make_preflight_response)
        self.add_after_request_func(CORS.set_cors_headers)
