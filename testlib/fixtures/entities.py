__all__ = [
    "ALERT_EXPECTED_END_DT",
    "ALERT_EXPECTED_START_DT",
    "BASIC_AUTH_USER_PASSWORD",
    "DATASET_ID",
    "INSTANCE_ALERT_ID",
    "INSTANCE_ID",
    "JOURNEY_ID",
    "PIPELINE_ID",
    "PROJECT_ID",
    "RUN_ALERT_ID",
    "RUN_ID",
    "action",
    "auth_provider",
    "basic_auth_user",
    "batch_end_schedule",
    "batch_start_schedule",
    "company",
    "component",
    "dag_simple",
    "dataset",
    "event_entity",
    "event_entity_2",
    "instance",
    "instance_alert",
    "instance_alert_components",
    "instance_instance_set",
    "instance_rule_end",
    "instance_rule_pipeline_end",
    "instance_rule_pipeline_start",
    "instance_rule_start",
    "journey",
    "journey_2",
    "organization",
    "patched_instance_set",
    "pending_run",
    "pipeline",
    "pipeline_2",
    "project",
    "rule",
    "run",
    "run_alert",
    "run_task",
    "server",
    "stream",
    "task",
    "test_db",
    "test_outcome",
    "testgen_dataset_component",
    "user",
    "obs_api_sa_key",
    "events_api_sa_key",
    "role",
    "service_account_key",
    "project_2",
    "journey_dag_edge",
    "admin_user",
]

import base64
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

import pytest

from common.auth.keys.lib import hash_value
from common.auth.keys.service_key import generate_key
from common.constants import ADMIN_ROLE
from common.constants.defaults import SCHEDULE_START_CRON_TIMEZONE
from common.entities import (
    DB,
    Action,
    Agent,
    AlertLevel,
    ApiEventType,
    AuthProvider,
    Company,
    Component,
    Dataset,
    EventEntity,
    EventVersion,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceAlertType,
    InstanceRule,
    InstanceRuleAction,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Organization,
    Pipeline,
    Project,
    Role,
    Rule,
    Run,
    RunAlert,
    RunAlertType,
    RunStatus,
    RunTask,
    Schedule,
    ScheduleExpectation,
    Server,
    Service,
    StreamingPipeline,
    Task,
    TestgenDatasetComponent,
    TestGenTestOutcomeIntegration,
    TestOutcome,
    User,
    UserRole,
)
from conf import init_db

AGENT_ID: UUID = UUID("fdcf7927-a43e-41ad-b8eb-e45d7b1a4d1a")
"""Default agent_id."""

PROJECT_ID: UUID = UUID("3a6042d6-41dd-441e-b0bc-a5127a07f04f")
"""Default project_id."""

JOURNEY_ID: UUID = UUID("04d043ce-9a8f-4dbf-b63e-ce05293da9ff")
"""Default journey_id."""

INSTANCE_ID: UUID = UUID("82bbef42-a159-414a-998f-24160f278621")
"""Default journey_id."""

COMPONENT_ID: UUID = UUID("af544cb4-4956-4942-a6f8-6a6268aaeb37")
"""Default component_id."""

PIPELINE_ID: UUID = UUID("98ef2265-8835-4356-a57b-b04b6cdf38d3")
"""Default pipeline_id."""

RUN_ID: UUID = UUID("e7d7e205-f1e6-4c1b-9a41-a29c2695fd58")
"""Default run_id."""

DATASET_ID: UUID = UUID("fd3cf898-c147-467f-9200-4c97c2899689")
"""Default dataset_id."""

INSTANCE_ALERT_ID: UUID = UUID("ab0c4a45-ca48-4a45-b031-c496e1f10131")
"""Default instance alert ID."""

RUN_ALERT_ID: UUID = UUID("f99bedf6-7f19-4300-b798-fe04a5138a4e")
"""Default run alert ID."""

TEST_OUTCOME_ID: UUID = UUID("9f6706b6-1ef2-4c7e-827a-372ef404c579")
"""Default test outcome ID."""

TEST_OUTCOME_INTEGRATION_2_ID = UUID("8208643d-56f3-4aef-89b3-839be6c55c97")
"""ID for test_outcome_integration_2 fixture."""

TEST_OUTCOME_INTEGRATION_1_ID = UUID("4820da79-6807-4409-9ec2-06c9ae09a88b")
"""ID for test_outcome_integration_1 fixture."""

BASIC_AUTH_USER_PASSWORD: str = "abcxyz12345"
"""Password for the user enabled to use basic authentication."""


@pytest.fixture()
def test_db():
    yield init_db()
    DB.close()


@pytest.fixture()
def company(test_db):
    return Company.create(name="C1")


@pytest.fixture()
def role(test_db):
    return Role.create(name="Test Role")


@pytest.fixture()
def auth_provider(company):
    return AuthProvider.create(
        client_id="a client id",
        client_secret="a client secret",
        discovery_doc_url="a doc url",
        domain="testdomain.com",
        company=company,
    )


@pytest.fixture()
def user(test_db, company):
    return User.create(name="U1", email="u@e.dev", primary_company=company)


@pytest.fixture()
def basic_auth_user(test_db, company):
    salt = b"baz"
    password = base64.b64encode(hash_value(value=BASIC_AUTH_USER_PASSWORD, salt=salt.decode("utf8"))).decode()
    return User.create(
        name="U2",
        email="u2@e.dev",
        primary_company=company,
        username="u2username",
        password=password,
        salt=base64.b64encode(salt),
    )


@pytest.fixture
def admin_role(test_db) -> Role:
    role, _ = Role.get_or_create(name=ADMIN_ROLE)
    yield role


@pytest.fixture
def admin_user(admin_role, company):
    user = User.create(name="admin", email="admin@e.dev", primary_company=company)
    UserRole.get_or_create(user=user, role=admin_role)
    yield user


@pytest.fixture()
def organization(test_db, company, user):
    return Organization.create(name="O1", company=company, created_by=user)


@pytest.fixture()
def project(test_db, organization, user):
    return Project.create(id=PROJECT_ID, name="P1", organization=organization, active=True, created_by=user)


@pytest.fixture()
def project_2(test_db, organization, user):
    return Project.create(id=uuid.uuid4(), name="P2", organization=organization, active=True, created_by=user)


@pytest.fixture()
def obs_api_sa_key(test_db, project):
    return generate_key(project=project, allowed_services=[Service.OBSERVABILITY_API.value])


@pytest.fixture()
def events_api_sa_key(test_db, project):
    return generate_key(project=project, allowed_services=[Service.EVENTS_API.value])


@pytest.fixture()
def service_account_key(test_db, obs_api_sa_key):
    return obs_api_sa_key.key_entity


@pytest.fixture()
def component(test_db, project, user):
    return Component.create(
        id=COMPONENT_ID, name="component-1", key="component-key-1", type="DATASET", project=project, created_by=user
    )


@pytest.fixture()
def journey(test_db, project, user):
    return Journey.create(id=JOURNEY_ID, name="J1", project=project, created_by=user)


@pytest.fixture()
def journey_2(test_db, project, user):
    return Journey.create(name="J2", project=project, created_by=user)


@pytest.fixture()
def pipeline(test_db, project, user):
    return Pipeline.create(
        id=PIPELINE_ID,
        name="Pipe 1",
        key="P1",
        project=project,
        created_by=user,
        tool="TEST_BATCH_PIPELINE_TOOL",
    )


@pytest.fixture()
def pipeline_2(test_db, project, user):
    return Pipeline.create(name="Pipe 2", key="P2", project=project, created_by=user)


@pytest.fixture()
def run(test_db, pipeline):
    return Run.create(id=RUN_ID, key="R1", pipeline=pipeline, status=RunStatus.RUNNING.name)


@pytest.fixture()
def pending_run(test_db, pipeline):
    return Run.create(key=None, start_time=None, pipeline=pipeline, status=RunStatus.PENDING.name)


@pytest.fixture()
def task(test_db, pipeline):
    return Task.create(name="Task 1", key="T1", pipeline=pipeline)


@pytest.fixture()
def run_task(test_db, task, run):
    return RunTask.create(task=task, run=run)


@pytest.fixture()
def dataset(test_db, project, user):
    return Dataset.create(
        id=DATASET_ID, name="Dataset 1", key="D1", project=project, created_by=user, tool="TEST_DATASET_TOOL"
    )


@pytest.fixture()
def server(test_db, project, user):
    return Server.create(key="S1", project=project, created_by=user, tool="TEST_SERVER_TOOL")


@pytest.fixture()
def stream(test_db, project, user):
    return StreamingPipeline.create(key="SP1", project=project, created_by=user, tool="TEST_STREAM_TOOL")


@pytest.fixture()
def dag_simple(test_db, journey, pipeline, dataset, server, stream):
    return [
        JourneyDagEdge.create(journey=journey, right=pipeline),
        JourneyDagEdge.create(journey=journey, right=dataset),
        JourneyDagEdge.create(journey=journey, right=server),
        JourneyDagEdge.create(journey=journey, right=stream),
    ]


@pytest.fixture()
def journey_dag_edge(test_db, journey, pipeline_2):
    return JourneyDagEdge.create(journey=journey, right=pipeline_2)


@pytest.fixture()
def action(test_db, company):
    return Action.create(name="A1", company=company, action_impl="some action")


@pytest.fixture()
def rule(test_db, pipeline, journey):
    return Rule.create(component=pipeline, journey=journey, rule_schema="simple_v1", rule_data={}, action="SEND_EMAIL")


@pytest.fixture()
def instance(test_db, journey):
    return Instance.create(id=INSTANCE_ID, journey=journey)


@pytest.fixture()
def instance_instance_set(instance, patched_instance_set):
    return list(InstanceSet.get_or_create([instance.id]).iis).pop()


@pytest.fixture()
def patched_instance_set(test_db):
    def sqlite_get_or_create(instance_ids):
        if not instance_ids:
            raise ValueError()

        is_query = (
            InstanceSet.select(InstanceSet, InstancesInstanceSets)
            .join(InstancesInstanceSets)
            .where(InstancesInstanceSets.instance << instance_ids)
        )

        for instance_set in is_query:
            if set(iis.instance_id for iis in instance_set.iis) == {*instance_ids}:
                return instance_set

        new_instance_set = InstanceSet.create()
        InstancesInstanceSets.bulk_create(
            [InstancesInstanceSets(instance=instance_id, instance_set=new_instance_set) for instance_id in instance_ids]
        )
        return new_instance_set

    with patch("common.entities.instance.InstanceSet.get_or_create") as mock:
        mock.side_effect = sqlite_get_or_create
        yield mock


@pytest.fixture()
def instance_rule_pipeline_start(test_db, journey, pipeline):
    return InstanceRule.create(journey=journey, action=InstanceRuleAction.START, batch_pipeline=pipeline)


@pytest.fixture()
def instance_rule_pipeline_end(test_db, journey, pipeline):
    return InstanceRule.create(journey=journey, action=InstanceRuleAction.END, batch_pipeline=pipeline)


@pytest.fixture()
def instance_rule_start(test_db, journey, pipeline):
    return InstanceRule.create(journey=journey, action=InstanceRuleAction.START, expression="* * * * *")


@pytest.fixture()
def instance_rule_end(test_db, journey, pipeline):
    return InstanceRule.create(journey=journey, action=InstanceRuleAction.END, expression="* * * * *")


@pytest.fixture
def batch_start_schedule(pipeline):
    return Schedule.create(
        schedule="* * * * *",
        expectation=ScheduleExpectation.BATCH_PIPELINE_START_TIME.name,
        timezone=SCHEDULE_START_CRON_TIMEZONE,
        component=pipeline,
    )


@pytest.fixture
def batch_end_schedule(pipeline):
    return Schedule.create(
        schedule="* * * * *",
        expectation=ScheduleExpectation.BATCH_PIPELINE_END_TIME.name,
        timezone=SCHEDULE_START_CRON_TIMEZONE,
        component=pipeline,
    )


ALERT_EXPECTED_START_DT: datetime = datetime(2005, 8, 13, 4, 2, 4, 2, tzinfo=timezone.utc)
"""The datetime of the expected_start_time for alert fixtures."""


ALERT_EXPECTED_END_DT: datetime = datetime(2005, 8, 13, 8, 4, 8, 1, tzinfo=timezone.utc)
"""The datetime of the expected_end_time for alert fixtures."""


@pytest.fixture()
def instance_alert(instance):
    alert = InstanceAlert.create(
        id=INSTANCE_ALERT_ID,
        instance=instance,
        name="instance-alert-1",
        description="a lovely instance-alert-1",
        message="instance-alert-1 was generated",
        level=AlertLevel.WARNING,
        type=InstanceAlertType.OUT_OF_SEQUENCE,
    )
    # Use the setters to populate the details dict
    alert.expected_start_time = ALERT_EXPECTED_START_DT
    alert.expected_end_time = ALERT_EXPECTED_END_DT
    alert.save(only=["details"])
    return alert


@pytest.fixture()
def run_alert(run, instance_instance_set):
    alert = RunAlert.create(
        id=RUN_ALERT_ID,
        run=run,
        name="run-alert-1",
        description="a lovely run-alert-1",
        level=AlertLevel.ERROR,
        type=RunAlertType.UNEXPECTED_STATUS_CHANGE,
    )
    # Use the setters to populate the details dict
    alert.expected_start_time = ALERT_EXPECTED_START_DT
    alert.expected_end_time = ALERT_EXPECTED_END_DT
    alert.save(only=["details"])
    run.update({Run.instance_set: instance_instance_set.instance_set}).execute()
    return alert


@pytest.fixture()
def test_outcome(component, run, task):
    return TestOutcome.create(
        id=TEST_OUTCOME_ID,
        component=component,
        description="Testy McTestface",
        dimensions=["a", "b", "c"],
        start_time=datetime(2000, 3, 9, 12, 11, 10, tzinfo=timezone.utc),
        end_time=datetime(2000, 3, 9, 13, 12, 11, tzinfo=timezone.utc),
        name="test-outcome-1",
        external_url="https://fake.testy/do-not-go-here",
        key="test-outcome-key-1",
        min_threshold=Decimal("3.14159"),
        max_threshold=Decimal("6.28318"),
        metric_value=Decimal("0.99999"),
        result="test-outcome-result-1",
        run=run,
        status="test-outcome-status-1",
        task=task,
        type="test-outcome-type-1",
        metric_name="some-metric",
        metric_description="This is a metric description",
    )


@pytest.fixture()
def test_outcome_integration_1(test_outcome):
    return TestGenTestOutcomeIntegration.create(
        id=TEST_OUTCOME_INTEGRATION_1_ID,
        test_outcome=test_outcome,
        columns=["a", "b"],
        test_parameters=[{"name": "attr-1", "value": 1.0}, {"name": "attr-2", "value": "v1"}],
        version=1,
        test_suite="test-suite-1",
        table="table-1",
    )


@pytest.fixture()
def test_outcome_integration_2(test_outcome):
    return TestGenTestOutcomeIntegration.create(
        id=TEST_OUTCOME_INTEGRATION_2_ID,
        test_outcome=test_outcome,
        columns=["d", "c"],
        test_parameters=[{"name": "attr-3", "value": 1.0}, {"name": "attr-4", "value": "v1"}],
        version=1,
        test_suite="test-suite-2",
        table="table-2",
    )


@pytest.fixture
def instance_alert_components(instance_alert, pipeline, pipeline_2):
    iac = [
        InstanceAlertsComponents.create(instance_alert=instance_alert, component=pipeline),
        InstanceAlertsComponents.create(instance_alert=instance_alert, component=pipeline_2),
    ]
    return iac


@pytest.fixture
def testgen_dataset_component(test_db, dataset):
    dataset_component = TestgenDatasetComponent.create(
        database_name="dataset-component-db-d4b66e29",
        connection_name="dataset-component-connection-d4b66e29",
        schema="dataset-component-schema-d4b66e29",
        table_list=["a", "b", "c"],
        table_group_id="c28c9306-fa91-4a3f-8f29-36d56c447c81",
        project_code="dataset-project-code-d4b66e29",
        component=dataset,
    )
    yield dataset_component


AGENT_LATEST_EVENT = datetime(2023, 10, 17, 12, 33, 19, 154295, tzinfo=timezone.utc)
"""Default timestamp for latest event received by an agent."""

AGENT_LATEST_HEARTBEAT = datetime(2023, 10, 17, 12, 42, 42, 424242, tzinfo=timezone.utc)
"""Default timestamp for the lasttime an agent checked-in."""


@pytest.fixture()
def agent_1(test_db, project):
    return Agent.create(
        project=project,
        key="test-agent-1-key",
        tool="test-agent-1-tool",
        version="1.0.0",
        lastest_heartbeat=AGENT_LATEST_HEARTBEAT,
        latest_event_timestamp=AGENT_LATEST_EVENT,
    )


@pytest.fixture()
def agent_2(test_db, project):
    dt_1 = datetime.now(timezone.utc)
    dt_2 = dt_1 + timedelta(seconds=42)
    return Agent.create(
        project=project,
        key="test-agent-2-key",
        tool="test-agent-2-tool",
        version="2.0.0",
        lastest_heartbeat=dt_2,
        latest_event_timestamp=dt_1,
    )


@pytest.fixture()
def event_entity(test_db, pipeline, task, run, run_task, instance_instance_set):
    return EventEntity.create(
        version=EventVersion.V2,
        type=ApiEventType.BATCH_PIPELINE_STATUS,
        created_timestamp=datetime(2024, 1, 20, 10, 0, 0, tzinfo=timezone.utc),
        timestamp=datetime(2024, 1, 20, 9, 59, 0, tzinfo=timezone.utc),
        project=pipeline.project_id,
        component=pipeline,
        task=task,
        run=run,
        run_task=run_task,
        instance_set=instance_instance_set.instance_set_id,
        v2_payload={},
    )


@pytest.fixture()
def event_entity_2(test_db, dataset):
    return EventEntity.create(
        version=EventVersion.V2,
        type=ApiEventType.DATASET_OPERATION,
        created_timestamp=datetime(2024, 1, 20, 9, 55, 0, tzinfo=timezone.utc),
        project=dataset.project_id,
        component=dataset,
        v2_payload={},
    )
