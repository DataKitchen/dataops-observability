__all__ = ["build_v1_routes", "build_event_routes"]

from typing import Callable

from flask import Blueprint, Flask

from event_api.endpoints.v1 import DatasetOperation, MessageLog, MetricLog, RunStatus, TestOutcomes

"""
Blueprints:  https://flask.palletsprojects.com/en/2.0.x/blueprints/
MethodView:  https://flask.palletsprojects.com/en/2.0.x/views/#method-views-for-apis
             https://flask.palletsprojects.com/en/2.0.x/api/#flask.views.MethodView
"""


def build_event_routes(bp: Blueprint) -> list[Callable]:
    dataset_operation_view = DatasetOperation.as_view("dataset-operation")
    message_log_view = MessageLog.as_view("message-log")
    metric_log_view = MetricLog.as_view("metric-log")
    status_view = RunStatus.as_view("run-status")
    test_outcomes_view = TestOutcomes.as_view("test-outcomes")

    bp.add_url_rule("/dataset-operation", view_func=dataset_operation_view, methods=["POST"])
    bp.add_url_rule("/message-log", view_func=message_log_view, methods=["POST"])
    bp.add_url_rule("/metric-log", view_func=metric_log_view, methods=["POST"])
    bp.add_url_rule("/run-status", view_func=status_view, methods=["POST"])
    bp.add_url_rule("/test-outcomes", view_func=test_outcomes_view, methods=["POST"])
    return [
        dataset_operation_view,
        message_log_view,
        metric_log_view,
        status_view,
        test_outcomes_view,
    ]


def build_v1_routes(app: Flask, prefix: str) -> list[Callable]:
    v1_bp = Blueprint("v1", __name__, url_prefix=f"/{prefix}/v1")
    views = build_event_routes(v1_bp)
    app.register_blueprint(v1_bp)
    return views
