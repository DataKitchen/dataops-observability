import logging
from http import HTTPStatus
from typing import Any, Callable

from flask import Blueprint, Flask, Response, make_response
from flask.views import MethodView

LOG = logging.getLogger(__name__)


class LivelinessProbe(MethodView):
    def get(self) -> Response:
        return make_response({}, HTTPStatus.OK)


class ReadinessProbe(MethodView):
    def __init__(self, callback: Callable[[], Any]):
        self.callback = callback

    def get(self) -> Response:
        try:
            self.callback()
        except Exception as e:
            LOG.warning("Readiness probe failed: %s", e)
            return make_response({}, HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            return make_response({}, HTTPStatus.OK)


class Health:
    def __init__(self, app: Flask, /, prefix: str, readiness_callback: Callable[[], Any]):
        """
        Adds the health check endpoints for kubernetes within their own blueprint.

        :param app: Flask App instance
        :param prefix: URL prefix for the health endpoints
        :param readiness_callback: Callable to be called every time a readiness probe is requested. Doesn't receive
               any arguments and must raise an Exception when the app shouldn't be considered ready
        """
        if not prefix:
            raise ValueError("You must provide a 'prefix' to the Health extension")
        self.app = app
        self.prefix = prefix
        self.readiness_callback = readiness_callback
        if app is not None:
            self.init_app()

    def init_app(self) -> None:
        # Because our APIs all live in the same domain, the health/ready endpoints need to be unique paths
        if self.app is not None:
            bp = Blueprint("health", __name__, url_prefix=f"/{self.prefix}")
            ready_view = ReadinessProbe.as_view("readyz", callback=self.readiness_callback)
            bp.add_url_rule("/readyz", view_func=ready_view, methods=["GET"])
            live_view = LivelinessProbe.as_view("livez")
            bp.add_url_rule("/livez", view_func=live_view, methods=["GET"])
            self.app.register_blueprint(bp)
