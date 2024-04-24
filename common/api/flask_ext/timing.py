__all__ = ["Timing"]
import logging
from datetime import datetime
from timeit import default_timer
from typing import Any

from flask import Response, g, request, request_finished, request_started
from flask.typing import ResponseReturnValue

from common.api.flask_ext.base_extension import BaseExtension

LOG = logging.getLogger(__name__)


class Timing(BaseExtension):
    @staticmethod
    def start_endpoint_timer(_: Any) -> None:
        g.request_start_time = default_timer()

    @staticmethod
    def end_endpoint_timer(_: Any, response: Response, **extra: Any) -> ResponseReturnValue:
        end_time = default_timer()
        try:
            email = g.user.email
        except AttributeError:
            email = "Unknown"
        data = {
            "title": "Endpoint timing",
            "user": email,
            "endpoint": request.path,
            "method": request.method.upper(),
            "date": datetime.now().isoformat(),
            "elapsed_time": f"{end_time - g.request_start_time}",
        }
        LOG.info(
            "[{date}] {user} calling [{method} {endpoint}] completed  (elapsed: {elapsed_time})".format(**data),
            extra=data,
        )
        return response

    def init_app(self) -> None:
        request_started.connect(Timing.start_endpoint_timer, self.app)
        request_finished.connect(Timing.end_endpoint_timer, self.app)
