from unittest.mock import Mock

import pytest
from marshmallow import ValidationError
from werkzeug.exceptions import Forbidden

from common.api.flask_ext import exception_handling as HandlerModule
from common.api.flask_ext.exception_handling import ExceptionHandling


@pytest.fixture
def mock_logger():
    old_logger = HandlerModule.LOG
    mock = Mock()
    mock.exception = Mock()
    HandlerModule.LOG = mock
    yield mock
    HandlerModule.LOG = old_logger


@pytest.fixture
def mock_make_response():
    old_make_response = HandlerModule.make_response
    mock = Mock(return_value="make_response")
    HandlerModule.make_response = mock
    yield mock
    HandlerModule.make_response = old_make_response


@pytest.mark.unit
def test_handle_exceptions(mock_logger, mock_make_response):
    e = Exception("unit test")
    result = ExceptionHandling.handle_exceptions(e)
    assert result == "make_response"
    mock_logger.exception.assert_called_once()
    mock_make_response.assert_called_once()
    response = mock_make_response.call_args_list[0][0][0]
    assert "error" in response and "An error has occurred" in response["error"]
    assert "error_id" in response
    assert "extra" in mock_logger.exception.call_args.kwargs
    assert "error_id" in mock_logger.exception.call_args.kwargs["extra"]
    assert str(response["error_id"]) == str(mock_logger.exception.call_args.kwargs["extra"]["error_id"])


@pytest.mark.unit
def test_handle_http_errors(mock_make_response):
    e = Forbidden(description="unit test")
    result = ExceptionHandling.handle_http_errors(e)
    assert result == "make_response"
    mock_make_response.assert_called_once()
    response = mock_make_response.call_args_list[0][0][0]
    assert "details" in response and response["details"] == {}


@pytest.mark.unit
def test_handle_http_errors_with_details(mock_make_response):
    e = Forbidden(description="unit test")
    setattr(e, "details", {"foo": "bar"})
    result = ExceptionHandling.handle_http_errors(e)
    assert result == "make_response"
    mock_make_response.assert_called_once()
    response = mock_make_response.call_args_list[0][0][0]
    assert "details" in response and response["details"] == {"foo": "bar"}


@pytest.mark.unit
def test_handle_deserialization_errors(mock_make_response):
    e = ValidationError("foobar")
    e.messages = "foobar"
    result = ExceptionHandling.handle_deserialization_errors(e)
    assert result == "make_response"
    mock_make_response.assert_called_once()
    response = mock_make_response.call_args_list[0][0][0]
    assert "details" in response and response["details"] == "foobar"
