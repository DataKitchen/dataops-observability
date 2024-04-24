__all__ = ["ExceptionHandling"]
import logging
from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

from flask import make_response
from flask.typing import ResponseReturnValue
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, HTTPException

from common.api.flask_ext.base_extension import BaseExtension

LOG = logging.getLogger(__name__)


class ExceptionHandling(BaseExtension):
    @staticmethod
    def handle_exceptions(e: Exception) -> ResponseReturnValue:
        # Either we got a different exception somehow or they didn't build the Exception right
        exc_id = uuid4()
        LOG.exception("500 Internal Server Error", extra={"error_id": exc_id})
        details = {"timestamp": datetime.now().isoformat(), "message": repr(e)}
        return make_response(
            {
                "error": "An error has occurred; consult the application logs for more details.",
                "error_id": exc_id,
                "details": details,
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @staticmethod
    def handle_http_errors(e: HTTPException) -> ResponseReturnValue:
        """
        Default Flask error handling spits out HTML pages.  We want to override that to just use JSON responses.
        Werkzeug errors do not have any room for "additional info", so we had to monkey patch a `details` onto it where
        we found it useful to add other information to the error response.
        """
        response: dict[str, object] = {"error": e.description, "details": {}}
        if hasattr(e, "details"):
            response["details"] = getattr(e, "details")
        return make_response(response, e.code)

    @staticmethod
    def handle_deserialization_errors(e: ValidationError) -> ResponseReturnValue:
        err = BadRequest(description="Invalid request data.")
        # quick patch to allow more information into the response body
        setattr(err, "details", e.messages)
        return ExceptionHandling.handle_http_errors(err)

    def init_app(self) -> None:
        self.app.register_error_handler(Exception, ExceptionHandling.handle_exceptions)
        self.app.register_error_handler(HTTPException, ExceptionHandling.handle_http_errors)
        self.app.register_error_handler(ValidationError, ExceptionHandling.handle_deserialization_errors)
