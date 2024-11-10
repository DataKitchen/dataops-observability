__all__ = ("build_v1_routes",)

from collections.abc import Callable

from flask import Blueprint, Flask

from agent_api.endpoints.v1 import Heartbeat

"""
Blueprints:  https://flask.palletsprojects.com/en/2.0.x/blueprints/
MethodView:  https://flask.palletsprojects.com/en/2.0.x/views/#method-views-for-apis
             https://flask.palletsprojects.com/en/2.0.x/api/#flask.views.MethodView
"""


def build_v1_routes(app: Flask, prefix: str) -> list[Callable]:
    v1_bp = Blueprint("v1", __name__, url_prefix=f"/{prefix}/v1")

    heartbeat_view = Heartbeat.as_view("agent-heartbeat")
    v1_bp.add_url_rule("/heartbeat", view_func=heartbeat_view, methods=["POST"])

    app.register_blueprint(v1_bp)
    return [heartbeat_view]
