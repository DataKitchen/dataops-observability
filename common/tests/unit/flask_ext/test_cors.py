import pytest
from flask import Response

from common.api.flask_ext.cors import CORS, CORS_HEADERS

CORS_HEADER_TUPLE: tuple[str, ...] = tuple(CORS_HEADERS.keys())


@pytest.mark.unit
def test_headers_added():
    response = Response()
    CORS.set_cors_headers(response)
    for header_name in CORS_HEADER_TUPLE:
        assert header_name in response.headers
