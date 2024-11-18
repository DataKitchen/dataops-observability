__all__ = ["build_v2_routes", "build_event_routes"]

from collections.abc import Callable

from flask import Blueprint, Flask

from event_api.endpoints.v2 import (
    BatchPipelineStatusView,
    DatasetOperationView,
    MessageLogView,
    MetricLogView,
    TestOutcomesView,
)

"""
Blueprints:  https://flask.palletsprojects.com/en/2.0.x/blueprints/
MethodView:  https://flask.palletsprojects.com/en/2.0.x/views/#method-views-for-apis
             https://flask.palletsprojects.com/en/2.0.x/api/#flask.views.MethodView
"""


def build_event_routes(bp: Blueprint) -> list[Callable]:
    dataset_operation_view = DatasetOperationView.as_view("dataset-operation")
    message_log_view = MessageLogView.as_view("message-log")
    metric_log_view = MetricLogView.as_view("metric-log")
    status_view = BatchPipelineStatusView.as_view("run-status")
    test_outcomes_view = TestOutcomesView.as_view("test-outcomes")

    bp.add_url_rule("/batch-pipeline-status", view_func=status_view, methods=["POST"])
    bp.add_url_rule("/dataset-operation", view_func=dataset_operation_view, methods=["POST"])
    bp.add_url_rule("/message-log", view_func=message_log_view, methods=["POST"])
    bp.add_url_rule("/metric-log", view_func=metric_log_view, methods=["POST"])
    bp.add_url_rule("/test-outcomes", view_func=test_outcomes_view, methods=["POST"])

    return [dataset_operation_view, status_view, message_log_view, metric_log_view, test_outcomes_view]


def build_v2_routes(app: Flask, prefix: str) -> list[Callable]:
    v2_bp = Blueprint("v2", __name__, url_prefix=f"/{prefix}/v2")
    views = build_event_routes(v2_bp)
    app.register_blueprint(v2_bp)
    return views
