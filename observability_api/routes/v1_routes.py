from typing import Callable

from flask import Blueprint, Flask

from common.api.search_view import add_route_with_search
from common.plugins import PluginManager
from observability_api.endpoints.v1.actions import Actions, ActionById
from observability_api.endpoints.v1.agents import Agents
from observability_api.endpoints.v1.alerts import ProjectAlerts
from observability_api.endpoints.v1.auth import BasicLogin, Logout
from observability_api.endpoints.v1.batch_pipelines import BatchPipelineComponentById, BatchPipelineComponents
from observability_api.endpoints.v1.companies import CompanyById
from observability_api.endpoints.v1.components import ComponentById, Components, JourneyComponents
from observability_api.endpoints.v1.datasets import DatasetComponentById, DatasetComponents
from observability_api.endpoints.v1.instance_rules import InstanceRuleById, InstanceRuleCreate
from observability_api.endpoints.v1.instances import CompanyInstances, InstanceById, InstanceDag, Instances
from observability_api.endpoints.v1.journeys import JourneyById, JourneyDag, JourneyDagEdgeById, Journeys
from observability_api.endpoints.v1.organizations import OrganizationById, Organizations
from observability_api.endpoints.v1.projects import ProjectById, ProjectEvents, Projects
from observability_api.endpoints.v1.rules import RuleById, Rules
from observability_api.endpoints.v1.runs import RunById, Runs
from observability_api.endpoints.v1.schedules import ScheduleById, Schedules
from observability_api.endpoints.v1.servers import ServerComponentById, ServerComponents
from observability_api.endpoints.v1.service_account_keys import ServiceAccountKeyById, ServiceAccountKeys
from observability_api.endpoints.v1.streaming_pipelines import (
    StreamingPipelineComponentById,
    StreamingPipelineComponents,
)
from observability_api.endpoints.v1.tasks import RunTasks
from observability_api.endpoints.v1.test_outcomes import ProjectTests, TestOutcomeById
from observability_api.endpoints.v1.upcoming_instances import CompanyUpcomingInstances, UpcomingInstances
from observability_api.endpoints.v1.users import UserById, Users

"""
Blueprints:  https://flask.palletsprojects.com/en/2.0.x/blueprints/
MethodView:  https://flask.palletsprojects.com/en/2.0.x/views/#method-views-for-apis
             https://flask.palletsprojects.com/en/2.0.x/api/#flask.views.MethodView
"""

# Helper Type Alias
Views = list[Callable]

SUBCOMPONENTS_VIEWS = [BatchPipelineComponents, DatasetComponents, ServerComponents, StreamingPipelineComponents]
SUBCOMPONENT_BY_ID_VIEWS = [
    BatchPipelineComponentById,
    DatasetComponentById,
    ServerComponentById,
    StreamingPipelineComponentById,
]


def build_action_routes(bp: Blueprint) -> list[Callable]:
    actions_view = Actions.as_view("action")
    action_by_id_view = ActionById.as_view("action_by_id")
    bp.add_url_rule("/companies/<uuid:company_id>/actions", view_func=actions_view, methods=["GET"])
    bp.add_url_rule("/actions/<uuid:action_id>", view_func=action_by_id_view, methods=["PATCH"])
    return [actions_view, action_by_id_view]


def build_agent_routes(bp: Blueprint) -> list[Callable]:
    agents_view = Agents.as_view("agents")
    bp.add_url_rule("/projects/<uuid:project_id>/agents", view_func=agents_view, methods=["GET"])
    return [agents_view]


def build_auth_routes(bp: Blueprint) -> list[Callable]:
    logout_view = Logout.as_view("auth-logout")
    bp.add_url_rule("/auth/logout", view_func=logout_view, methods=["GET"])
    basic_login_view = BasicLogin.as_view("auth-basic-login")
    bp.add_url_rule("/auth/basic", view_func=basic_login_view, methods=["GET"])
    return [logout_view, basic_login_view]


def build_company_routes(bp: Blueprint) -> Views:
    company_by_id_view = CompanyById.as_view("company_by_id")
    bp.add_url_rule("/companies/<uuid:company_id>", view_func=company_by_id_view, methods=["GET"])
    return [company_by_id_view]


def build_instance_routes(bp: Blueprint) -> Views:
    instances_view = Instances.as_view("instances")
    instance_by_id_view = InstanceById.as_view("instance_by_id")
    instance_dag_view = InstanceDag.as_view("instance_dag")
    company_instances_view = CompanyInstances.as_view("company_instances")
    instance_search_view = add_route_with_search(
        bp,
        "/projects/<uuid:project_id>/instances",
        view_func=instances_view,
        methods=["GET"],
    )
    bp.add_url_rule("/instances/<uuid:instance_id>/dag", view_func=instance_dag_view, methods=["GET"])
    bp.add_url_rule("/instances/<uuid:instance_id>", view_func=instance_by_id_view, methods=["GET"])
    bp.add_url_rule("/instances", view_func=company_instances_view, methods=["GET"])
    return [instances_view, instance_search_view, instance_by_id_view, company_instances_view]


def build_instance_rule_routes(bp: Blueprint) -> Views:
    instance_rule_create = InstanceRuleCreate.as_view("instance-rule-create")
    bp.add_url_rule("/journeys/<uuid:journey_id>/instance-conditions", view_func=instance_rule_create, methods=["POST"])
    instance_rule_by_id = InstanceRuleById.as_view("instance-rule-by-id")
    bp.add_url_rule(
        "/instance-conditions/<uuid:instance_rule_id>",
        view_func=instance_rule_by_id,
        methods=["DELETE"],
    )
    return [instance_rule_by_id, instance_rule_create]


def build_journey_routes(bp: Blueprint) -> Views:
    journeys_view = Journeys.as_view("journeys")
    journey_by_id_view = JourneyById.as_view("journey_by_id")
    bp.add_url_rule("/projects/<uuid:project_id>/journeys", view_func=journeys_view, methods=["GET", "POST"])
    bp.add_url_rule("/journeys/<uuid:journey_id>", view_func=journey_by_id_view, methods=["DELETE", "GET", "PATCH"])
    return [journeys_view, journey_by_id_view]


def build_journey_dag_routes(bp: Blueprint) -> Views:
    journey_dag_view = JourneyDag.as_view("journey_dag")
    dag_edge_view = JourneyDagEdgeById.as_view("journey_dag_edge")
    bp.add_url_rule("/journeys/<uuid:journey_id>/dag", view_func=journey_dag_view, methods=["GET", "PUT"])
    bp.add_url_rule("/journey-dag-edge/<uuid:edge_id>", view_func=dag_edge_view, methods=["DELETE"])
    return [journey_dag_view, dag_edge_view]


def build_organization_routes(bp: Blueprint) -> Views:
    orgs_view = Organizations.as_view("organizations")
    org_by_id_view = OrganizationById.as_view("organization_by_id")
    bp.add_url_rule("/companies/<uuid:company_id>/organizations", view_func=orgs_view, methods=["GET"])
    bp.add_url_rule("/organizations/<uuid:organization_id>", view_func=org_by_id_view, methods=["GET"])
    return [orgs_view, org_by_id_view]


def build_project_routes(bp: Blueprint) -> Views:
    projects_view = Projects.as_view("projects")
    project_by_id = ProjectById.as_view("project_by_id")
    project_events = ProjectEvents.as_view("project_events")
    project_tests = ProjectTests.as_view("project_tests")
    project_alerts = ProjectAlerts.as_view("project_alerts")

    bp.add_url_rule("/organizations/<uuid:organization_id>/projects", view_func=projects_view, methods=["GET"])
    bp.add_url_rule("/projects/<uuid:project_id>", view_func=project_by_id, methods=["GET"])
    bp.add_url_rule("/projects/<uuid:project_id>/events", view_func=project_events, methods=["GET"])
    bp.add_url_rule("/projects/<uuid:project_id>/tests", view_func=project_tests, methods=["GET"])
    bp.add_url_rule("/projects/<uuid:project_id>/alerts", view_func=project_alerts, methods=["GET"])
    return [projects_view, project_by_id, project_events, project_tests, project_alerts]


def build_user_routes(bp: Blueprint) -> Views:
    users_view = Users.as_view("users")
    user_by_id_view = UserById.as_view("user_by_id")
    bp.add_url_rule("/users", view_func=users_view, methods=["GET"])
    bp.add_url_rule("/users/<uuid:user_id>", view_func=user_by_id_view, methods=["GET"])
    return [users_view, user_by_id_view]


def build_rules_routes(bp: Blueprint) -> Views:
    rules_view = Rules.as_view("rules")
    rules_by_id_view = RuleById.as_view("rules_by_id")
    bp.add_url_rule("/journeys/<uuid:journey_id>/rules", view_func=rules_view, methods=["GET", "POST"])
    bp.add_url_rule("/rules/<uuid:rule_id>", view_func=rules_by_id_view, methods=["DELETE", "GET", "PATCH"])
    return [rules_view, rules_by_id_view]


def build_run_routes(bp: Blueprint) -> Views:
    runs_view = Runs.as_view("runs")
    run_by_id_view = RunById.as_view("run_by_id")

    bp.add_url_rule("/projects/<uuid:project_id>/runs", view_func=runs_view, methods=["GET"])
    bp.add_url_rule("/runs/<uuid:run_id>", view_func=run_by_id_view, methods=["GET"])
    return [runs_view, run_by_id_view]


def build_task_routes(bp: Blueprint) -> Views:
    runtask_view = RunTasks.as_view("runtasks")
    bp.add_url_rule("/runs/<uuid:run_id>/tasks", view_func=runtask_view, methods=["GET"])
    return [runtask_view]


def build_service_account_key_routes(bp: Blueprint) -> Views:
    sa_key_view = ServiceAccountKeys.as_view("sa_key_view")
    sa_key_by_id_view = ServiceAccountKeyById.as_view("sa_key_by_id_view")
    bp.add_url_rule("/projects/<uuid:project_id>/service-account-key", view_func=sa_key_view, methods=["POST", "GET"])
    bp.add_url_rule("/service-account-key/<uuid:key_id>", view_func=sa_key_by_id_view, methods=["DELETE"])
    return [sa_key_view, sa_key_by_id_view]


def build_component_routes(bp: Blueprint) -> Views:
    components_view = Components.as_view("components")
    component_by_id_view = ComponentById.as_view("component_by_id")
    journey_components_view = JourneyComponents.as_view("journey_components")
    bp.add_url_rule("/projects/<uuid:project_id>/components", view_func=components_view, methods=["GET"])
    bp.add_url_rule(
        "/components/<uuid:component_id>", view_func=component_by_id_view, methods=["DELETE", "GET", "PATCH"]
    )
    bp.add_url_rule("/journeys/<uuid:journey_id>/components", view_func=journey_components_view, methods=["GET"])
    return [components_view, component_by_id_view, journey_components_view]


def build_upcoming_instance_routes(bp: Blueprint) -> Views:
    upcoming_instances_view = UpcomingInstances.as_view("upcoming_instances")
    company_upcoming_instances_view = CompanyUpcomingInstances.as_view("company_upcoming_instances")
    bp.add_url_rule(
        "/projects/<uuid:project_id>/upcoming-instances", view_func=upcoming_instances_view, methods=["GET"]
    )
    bp.add_url_rule("/upcoming-instances", view_func=company_upcoming_instances_view, methods=["GET"])
    return [upcoming_instances_view, company_upcoming_instances_view]


def build_subcomponent_routes(bp: Blueprint) -> Views:
    subcomponent_list_views = [v.add_route(bp, "/projects/<uuid:project_id>/{}") for v in SUBCOMPONENTS_VIEWS]
    subcomponent_by_id_views = [v.add_route(bp, "/{}/<uuid:component_id>") for v in SUBCOMPONENT_BY_ID_VIEWS]
    return [*subcomponent_list_views, *subcomponent_by_id_views]


def build_schedule_routes(bp: Blueprint) -> Views:
    schedules_view = Schedules.as_view("schedules")
    schedule_by_id_view = ScheduleById.as_view("schedule_by_id")
    bp.add_url_rule(
        "/components/<uuid:component_id>/schedules",
        view_func=schedules_view,
        methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/schedules/<uuid:schedule_id>",
        view_func=schedule_by_id_view,
        methods=["DELETE"],
    )
    return [schedules_view, schedule_by_id_view]


def build_test_outcomes_routes(bp: Blueprint) -> Views:
    test_outcomes_by_id_view = TestOutcomeById.as_view("test_outcomes_by_id")
    bp.add_url_rule(
        "/test-outcomes/<uuid:test_outcome_id>",
        view_func=test_outcomes_by_id_view,
        methods=["GET"],
    )
    return [test_outcomes_by_id_view]


def build_v1_routes(app: Flask, prefix: str, native_routes: bool = True, plugin_routes: bool = True) -> Views:
    bp = Blueprint("v1", __name__, url_prefix=f"/{prefix}/v1")
    views = []

    if native_routes:
        views += build_action_routes(bp)
        views += build_agent_routes(bp)
        views += build_auth_routes(bp)
        views += build_company_routes(bp)
        views += build_instance_routes(bp)
        views += build_instance_rule_routes(bp)
        views += build_journey_routes(bp)
        views += build_journey_dag_routes(bp)
        views += build_organization_routes(bp)
        views += build_project_routes(bp)
        views += build_rules_routes(bp)
        views += build_run_routes(bp)
        views += build_schedule_routes(bp)
        views += build_service_account_key_routes(bp)
        views += build_task_routes(bp)
        views += build_user_routes(bp)
        views += build_component_routes(bp)
        views += build_upcoming_instance_routes(bp)
        views += build_subcomponent_routes(bp)
        views += build_test_outcomes_routes(bp)

    if plugin_routes:
        PluginManager.load_all("observability_api_v1", bp, views)

    app.register_blueprint(bp)
    return views
