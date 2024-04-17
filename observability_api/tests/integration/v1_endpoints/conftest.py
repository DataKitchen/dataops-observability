import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from flask import Flask, g

from common.api.flask_ext.authentication import JWTAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.api.flask_ext.url_converters import URLConverters
from common.entities import (
    DB,
    AlertLevel,
    Company,
    InstanceAlertsComponents,
    JourneyDagEdge,
    Organization,
    Project,
    Role,
    Run,
    RunAlert,
    RunAlertType,
    StreamingPipeline,
    Task,
    TestOutcome,
    User,
    UserRole,
)
from common.events.v1 import TestStatuses
from conf import init_db
from observability_api.config.defaults import API_PREFIX
from observability_api.routes import build_v1_routes
from testlib.fixtures.entities import *

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


@pytest.fixture(autouse=True)
def local_patched_instance_set(patched_instance_set):
    yield patched_instance_set


@pytest.fixture(autouse=True)
def test_db():
    yield init_db()
    DB.close()


@pytest.fixture
def company_2():
    return Company.create(name="C2")


@pytest.fixture
def user_2(company_2):
    return User.create(name="U2", email="u2@e.dev", primary_company=company_2)


@pytest.fixture
def organization_2(company_2):
    return Organization.create(name="O2", company=company_2)


@pytest.fixture
def inactive_project(organization, user):
    return Project.create(name="InactiveProjectTest", organization=organization, active=False, created_by=user)


@pytest.fixture
def inactive_project_from_org(organization, user):
    return Project.create(
        name="InactiveProjectFromInactiveOrgTest", organization=organization, active=False, created_by=user
    )


@pytest.fixture
def project_2(organization_2):
    return Project.create(name="P2", organization=organization_2, active=True)


@pytest.fixture
def streaming_pipeline(project, user):
    return StreamingPipeline.create(key="StreamingPipeline", project=project, created_by=user)


@pytest.fixture
def tasks(pipeline):
    for key in (1, 2, 3):
        Task.create(key=f"test task{pipeline.id}-{key}", pipeline=pipeline)
    return Task.select().where(Task.pipeline == pipeline)


@pytest.fixture
def runs(pipeline):
    for key in ("1", "2", "3", "4", "5", "6"):
        r = Run.create(key=key, name=f"name{key}", pipeline=pipeline, status="COMPLETED")
        RunAlert.create(
            run=r,
            description=f"Alert for run {key}",
            name=f"key {key}",
            level=AlertLevel["ERROR"].value,
            type=RunAlertType["LATE_START"].value,
        )
    results = list(Run.select().where(Run.pipeline == pipeline))
    yield results


@pytest.fixture
def instance_alerts_components(client, instance, pipeline, pipeline_2, instance_alert):
    return [
        InstanceAlertsComponents.create(instance_alert=instance_alert, component=pipeline),
        InstanceAlertsComponents.create(instance_alert=instance_alert, component=pipeline_2),
    ]


@pytest.fixture
def journey_dag_edge(journey, pipeline):
    return JourneyDagEdge.create(journey=journey, left=None, right=pipeline)


@pytest.fixture
def instance_runs(instance_instance_set, runs):
    Run.update({"instance_set": instance_instance_set.instance_set}).where(Run.id << runs).execute()
    yield runs


@pytest.fixture
def run_alerts(runs, instance_runs):
    for index, r in enumerate(runs):
        RunAlert.create(
            name=f"alert {index}",
            description=f"Description of run alert {index}",
            level=AlertLevel["ERROR"].value,
            type=RunAlertType["LATE_END"].value,
            run=r,
        )
    yield RunAlert.select(RunAlert).join(Run).where(RunAlert.run.in_(runs))


@pytest.fixture
def run_tests(runs):
    for index, r in enumerate(runs):
        TestOutcome.create(
            name=f"test outcome {index}",
            status=TestStatuses.PASSED.name,
            run=r,
            component=r.pipeline,
            instance_set=r.instance_set,
        )
    yield TestOutcome.select(TestOutcome).where(TestOutcome.run.in_(runs))


@pytest.fixture
def test_user(company):
    yield User.create(id=uuid.uuid4(), name="Test User", email="testuser@domain.com", primary_company=company)


@pytest.fixture
def flask_app(test_user):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    Config(app, config_module="observability_api.config")
    os.makedirs(app.instance_path, exist_ok=True)
    # This has to go before route building. If it does not, the rules will not be affected.
    URLConverters(app)
    build_v1_routes(app, prefix=API_PREFIX)
    ExceptionHandling(app)
    yield app
    shutil.rmtree(app.instance_path, ignore_errors=True)


@pytest.fixture
def client(flask_app):
    with flask_app.app_context():
        with flask_app.test_client() as client:
            yield client


@pytest.fixture
def jwt_flask_app(flask_app):
    JWTAuth(flask_app)
    yield flask_app


@pytest.fixture
def jwt_client(jwt_flask_app):
    with jwt_flask_app.test_client() as client:
        with jwt_flask_app.app_context():
            yield client


@pytest.fixture
def g_observability_api_service(flask_app, obs_api_sa_key):
    @flask_app.before_request
    def set_allowed_services():
        g.allowed_services = obs_api_sa_key.key_entity.allowed_services

    return obs_api_sa_key


@pytest.fixture
def g_events_api_service(flask_app, events_api_sa_key):
    @flask_app.before_request
    def set_allowed_services():
        g.allowed_services = events_api_sa_key.key_entity.allowed_services

    return events_api_sa_key


@pytest.fixture
def g_project(flask_app, project):
    @flask_app.before_request
    def set_project():
        g.project = project

    return project


@pytest.fixture
def g_project_2(flask_app, project_2):
    @flask_app.before_request
    def set_project():
        g.project = project_2

    return project_2


@pytest.fixture
def g_user(flask_app, user):
    @flask_app.before_request
    def set_user():
        g.user = user

    return user


@pytest.fixture
def g_user_2(flask_app, user_2):
    @flask_app.before_request
    def set_user():
        g.user = user_2

    return user_2


@pytest.fixture
def admin_role():
    return Role.create(name="ADMIN")


@pytest.fixture
def g_user_2_admin(g_user_2, admin_role):
    return UserRole.create(user=g_user_2, role=admin_role)


@pytest.fixture
def subcomponent(request, pipeline, dataset, server, streaming_pipeline):
    subcomponent_dict = {
        "pipeline": pipeline,
        "dataset": dataset,
        "server": server,
        "streaming-pipeline": streaming_pipeline,
    }
    return subcomponent_dict[request.param]


@pytest.fixture
def test_outcome(client, instance_instance_set, instance_runs, pipeline):
    test_outcome = TestOutcome.create(
        name="Abc",
        description="Abc_Description",
        dimensions=["a", "b", "c"],
        status=TestStatuses.WARNING.name,
        run=instance_runs[0].id,
        start_time=datetime.now(tz=timezone.utc) - timedelta(minutes=15),
        end_time=datetime.now(tz=timezone.utc) - timedelta(minutes=5),
        component=pipeline,
        instance_set=instance_instance_set.instance_set,
        external_url="https://example.com",
        metric_value=Decimal("4.1"),
        min_threshold=Decimal("3.14"),
        max_threshold=Decimal("6.28"),
        result="test-outcome-result-v1-endpoint",
        type="test-outcome-type-v1-endpoint",
        key="test-outcome-key-v1-endpoint",
    )
    yield test_outcome


@pytest.fixture
def test_outcomes(client, instance_instance_set, pipeline):
    test_outcomes = []
    for i in range(2):
        test_outcome = TestOutcome.create(
            name=f"DKTest{i}",
            dimension=[f"a-{i}", f"b-{i}", f"c-{i}"],
            description=f"Description{i}",
            status=f"{TestStatuses.PASSED.name if i % 2 == 0 else TestStatuses.FAILED.name}",
            start_time=datetime.now(tz=timezone.utc) + timedelta(minutes=5 * i),
            end_time=datetime.now(tz=timezone.utc) + timedelta(minutes=15 * i),
            component=pipeline,
            instance_set=instance_instance_set.instance_set,
            external_url="https://example.com",
            result=f"test-outcome-result-v1-endpoint-{i}",
            type=f"test-outcome-type-v1-endpoint-{i}",
            key=f"test-outcome-key-v1-endpoint-{i}",
        )
        test_outcomes.append(test_outcome)
    yield test_outcomes
