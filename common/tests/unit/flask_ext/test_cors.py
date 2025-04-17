import flask
import pytest
from flask import Response

from common.api.flask_ext.cors import CORS, CORS_HEADERS

CORS_HEADER_TUPLE: tuple[str, ...] = tuple(CORS_HEADERS.keys())


@pytest.mark.unit
def test_headers_added_matching_domain():
    test_app = flask.Flask("test_flask_app")
    cors = CORS()

    matching_domains = ["https://xyz.com", "https://test.mydomain.com", "http://localhost:8080"]
    for domain in matching_domains:
        with test_app.test_request_context(headers={"Origin": domain}):
            response = Response()
            cors.set_cors_headers(response)
            assert response.headers["Access-Control-Allow-Origin"] is domain
            for header_name in CORS_HEADER_TUPLE:
                assert header_name in response.headers


@pytest.mark.unit
def test_no_headers_other_domain():
    test_app = flask.Flask("test_flask_app")
    cors = CORS()

    matching_domains = ["https://abc.com", "https://test.mydomain.com.io", "http://localhost"]
    for domain in matching_domains:
        with test_app.test_request_context(headers={"Origin": domain}):
            response = Response()
            cors.set_cors_headers(response)
            assert "Access-Control-Allow-Origin" not in response.headers
            for header_name in CORS_HEADER_TUPLE:
                assert header_name not in response.headers
