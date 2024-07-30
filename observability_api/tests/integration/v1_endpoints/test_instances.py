from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Optional
from uuid import UUID, uuid4

import pytest
from werkzeug.datastructures import MultiDict

from common.entities import (
    AlertLevel,
    Company,
    Dataset,
    DatasetOperation,
    DatasetOperationType,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceAlertType,
    InstanceSet,
    InstanceStatus,
    Journey,
    JourneyDagEdge,
    Organization,
    Pipeline,
    Project,
    Run,
    RunAlert,
    RunAlertType,
    RunStatus,
    TestOutcome,
)
from common.entities.instance import InstanceStartType
from common.entity_services.helpers import SortOrder
from common.entity_services.instance_service import ADDITIONAL_ALERT_DESCRIPTION
from common.events.enums import EventSources
from common.events.v1 import ApiRunStatus, RunStatusEvent, TestStatuses
from testlib.fixtures.entities import *


@dataclass(kw_only=True)
class AlertCount:
    error_ct: int
    warning_ct: int


@pytest.fixture
def test_outcome(client, instance_runs, pipeline):
    test_outcome = TestOutcome.create(
        name="Abc",
        description="Abc_Description",
        status=TestStatuses.WARNING.name,
        run=instance_runs[0].id,
        start_time=datetime.now(tz=timezone.utc) - timedelta(minutes=15),
        end_time=datetime.now(tz=timezone.utc) - timedelta(minutes=5),
        component=pipeline,
    )
    yield test_outcome


@pytest.fixture
def test_outcomes(client, instance_instance_set, pipeline):
    test_outcomes = []
    for i in range(2):
        test_outcome = TestOutcome.create(
            name=f"DKTest{i}",
            description=f"Description{i}",
            status=f"{TestStatuses.PASSED.name if i % 2 == 0 else TestStatuses.FAILED.name}",
            start_time=datetime.now(tz=timezone.utc) + timedelta(minutes=5 * i),
            end_time=datetime.now(tz=timezone.utc) + timedelta(minutes=15 * i),
            component=pipeline,
            instance_set=instance_instance_set.instance_set,
        )
        test_outcomes.append(test_outcome)
    yield test_outcomes


@pytest.fixture
def instances(client, journey):
    for _ in range(6):
        Instance.create(journey=journey)
    results = Instance.select().where(Instance.journey == journey)
    yield results


@pytest.fixture
def payload_instance(client, journey):
    return Instance.create(journey=journey, payload_key="p1", start_type=InstanceStartType.PAYLOAD)


@pytest.fixture
def instance_alerts(instances, pipeline, pipeline_2):
    for i, instance in enumerate(instances):
        alert = InstanceAlert.create(
            name=f"alert {i}",
            description=f"Description of instance {i}",
            level=AlertLevel["ERROR"].value,
            type=InstanceAlertType["LATE_END"].value,
            instance=instance,
        )
        InstanceAlertsComponents.create(instance_alert=alert, component=pipeline.id)
        if i == 1:
            InstanceAlertsComponents.create(instance_alert=alert, component=pipeline_2.id)
    yield InstanceAlert.select(InstanceAlert).join(Instance).where(InstanceAlert.instance.id.in_(instances))


class TestProjectContext:
    project: Project
    journey: Journey
    pipeline: Pipeline
    dataset: Dataset
    runs: list[Run]
    instances: list[Instance]
    instance_alerts: list[InstanceAlert]
    run_alerts: list[RunAlert]

    def __init__(
        self,
        org: Organization,
        name: str = "1",
        num_instances: int = 1,
        instance_alert_ct: AlertCount = AlertCount(error_ct=1, warning_ct=0),
        run_alert_ct: AlertCount = AlertCount(error_ct=1, warning_ct=0),
    ):
        self.project = Project.create(name=f"Project-{name}", organization=org, active=True)
        self.journey = Journey.create(name=f"Journey-{name}", project=self.project)
        self.pipeline = Pipeline.create(key=f"Pipeline-{name}", project=self.project)
        self.dataset = Dataset.create(key=f"Dataset-{name}", project=self.project)

        for i in range(num_instances):
            instance = Instance.create(journey=self.journey)
            instance_set = InstanceSet.get_or_create([instance.id])
            Run.create(
                key=f"Run-instance-{i}",
                pipeline=self.pipeline,
                project=self.project,
                status=RunStatus.RUNNING.value,
                instance_set=instance_set,
            )

        self.instances = list(Instance.select().where(Instance.journey == self.journey))
        self.runs = list(Run.select().where(Run.pipeline == self.pipeline))
        self.create_instance_alerts(self.instances, instance_alert_ct)
        self.instance_alerts = list(InstanceAlert.select().where(InstanceAlert.instance.in_(self.instances)))
        self.create_run_alerts(self.runs, run_alert_ct)
        self.run_alerts = list(RunAlert.select().where(RunAlert.run.in_(self.runs)))
        self.create_journey_dag(self.project, self.journey, self.pipeline, self.dataset)
        self.create_test_outcomes(self.instances, self.pipeline)
        self.create_dataset_operations(self.instances, self.dataset)

    @staticmethod
    def create_instance_alerts(instances: list[Instance], alert_ct: AlertCount):
        for i, instance in enumerate(instances, 1):
            alerts = [
                InstanceAlert(
                    name=f"instance {i} error alert {j}",
                    description=f"Description of instance {i} error alert {j}",
                    level=AlertLevel.ERROR.value,
                    type=InstanceAlertType["LATE_END"].value,
                    instance=instance,
                )
                for j in range(alert_ct.error_ct)
            ]
            alerts.extend(
                [
                    InstanceAlert(
                        name=f"instance {i} warning alert {j}",
                        description=f"Description of instance {i} warning alert {j}",
                        level=AlertLevel.WARNING.value,
                        type=InstanceAlertType["LATE_END"].value,
                        instance=instance,
                    )
                    for j in range(alert_ct.warning_ct)
                ]
            )
            InstanceAlert.bulk_create(alerts, batch_size=100)

    @staticmethod
    def create_run_alerts(runs: list[Run], alert_ct: AlertCount):
        for i, run in enumerate(runs, 1):
            alerts = [
                RunAlert(
                    name=f"run {i} error alert {j}",
                    description=f"Description of run {i} error alert {j}",
                    level=AlertLevel["ERROR"].value,
                    type=RunAlertType["LATE_END"].value,
                    run=run,
                )
                for j in range(alert_ct.error_ct)
            ]
            alerts.extend(
                [
                    RunAlert(
                        name=f"run {i} warning alert {j}",
                        description=f"Description of run {i} warning alert {j}",
                        level=AlertLevel.WARNING.value,
                        type=RunAlertType["LATE_END"].value,
                        run=run,
                    )
                    for j in range(alert_ct.warning_ct)
                ]
            )
            RunAlert.bulk_create(alerts, batch_size=100)

    @staticmethod
    def create_journey_dag(project: Project, journey: Journey, node_1: Pipeline, node_3: Dataset):
        node_2 = Pipeline.create(key="Batch-Pipeline-2", project=project)
        node_4 = Pipeline.create(key="Batch-Pipeline-4", project=project)
        node_5 = Pipeline.create(key="Batch-Pipeline-5", project=project)

        JourneyDagEdge.create(journey=journey, right=node_1)
        JourneyDagEdge.create(journey=journey, left=node_1, right=node_2)
        JourneyDagEdge.create(journey=journey, left=node_1, right=node_3)
        JourneyDagEdge.create(journey=journey, left=node_2, right=node_3)
        JourneyDagEdge.create(journey=journey, left=node_3, right=node_4)
        JourneyDagEdge.create(journey=journey, left=node_3, right=node_5)

    @staticmethod
    def create_test_outcomes(instances: list[Instance], component: Pipeline | Dataset):
        for instance in instances:
            instance_set = InstanceSet.get_or_create([instance.id])
            for i in range(3):
                TestOutcome.create(
                    name=f"DKTest{i}",
                    description=f"Description{i}",
                    status=f"{TestStatuses.PASSED.name if i % 2 == 0 else TestStatuses.FAILED.name}",
                    start_time=datetime.now(tz=timezone.utc) + timedelta(minutes=5 * i),
                    end_time=datetime.now(tz=timezone.utc) + timedelta(minutes=15 * i),
                    component=component,
                    instance_set=instance_set,
                )

    @staticmethod
    def create_dataset_operations(instances: list[Instance], dataset: Dataset):
        for instance in instances:
            instance_set = InstanceSet.get_or_create([instance.id])
            for i in range(3):
                DatasetOperation.create(
                    dataset=dataset,
                    instance_set=instance_set,
                    operation_time=datetime.now(tz=timezone.utc),
                    operation=f"{DatasetOperationType.READ.name if i % 2 == 0 else DatasetOperationType.WRITE.name}",
                    path="/path/to/file",
                )


@pytest.fixture
def run_status_event(pipeline, project, journey, instances):
    ts = datetime.now(timezone.utc)
    yield RunStatusEvent(
        project_id=project.id,
        event_id=uuid4(),
        pipeline_id=pipeline.id,
        run_key="run-correlation",
        run_id=uuid4(),
        task_key="task_key",
        task_id=UUID("185208fd-1062-4f4a-a59f-61f2db99c3d7"),
        task_name="My Task",
        source=EventSources.API.name,
        pipeline_key="4da46ac7-c318-4cbd-83bb-83edaa6044c5",
        pipeline_name="My Pipeline",
        received_timestamp=ts,
        event_timestamp=ts,
        external_url="https://example.com",
        run_task_id=UUID("c3fc7f3d-c3b1-4d08-8e98-439bc4918ce6"),
        metadata={"key": "value"},
        event_type="RunStatusEvent",
        status=ApiRunStatus.RUNNING.value,
        instances=[
            {"instance": instances[0].id, "journey": instances[0].journey_id},
            {"instance": instances[1].id, "journey": instances[1].journey_id},
        ],
        payload_keys=["p1", "p2"],
    )


@pytest.fixture
def runs_different_statuses(client, pipeline):
    desired = {
        "1": "COMPLETED",
        "2": "COMPLETED",
        "3": "COMPLETED",
        "4": "COMPLETED_WITH_WARNINGS",
        "5": "RUNNING",
        "6": "RUNNING",
    }
    return [Run.create(key=key, pipeline=pipeline, status=status) for key, status in desired.items()]


@pytest.fixture
def instance_runs_different_statuses(instance_instance_set, runs_different_statuses):
    for run in runs_different_statuses:
        run.instance_set = instance_instance_set.instance_set
        run.save()
    yield runs_different_statuses


@pytest.mark.integration
def test_list_instances_plain(
    client, journey, instances, instance_alerts, pipeline, pipeline_2, g_user, payload_instance
):
    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances")
    assert response.status_code == HTTPStatus.OK, response.json

    expected_total = instances.count()
    found_total = response.json["total"]

    assert expected_total == found_total, f"Got {found_total} runs but expected {expected_total}"
    instances = response.json["entities"]
    for instance in instances:
        if instance["payload_key"] is None:
            assert instance["journey"]["id"] == str(journey.id)
            assert instance["journey"]["name"] == journey.name
            assert instance["project"]["id"] == str(journey.project.id)
            assert instance["project"]["name"] == journey.project.name
            assert instance["start_time"] is not None
            assert instance["end_time"] is None
            assert instance["active"] is True
            assert instance["runs_summary"] == []
            assert len(instance["alerts_summary"]) == 1, instance["alerts_summary"]
            assert instance["alerts_summary"][0]["description"] == next(
                ia.description for ia in instance_alerts if instance["id"] == str(ia.instance.id)
            )
            assert instance["tests_summary"] == []
            assert instance["start_type"] == InstanceStartType.DEFAULT.value
        else:
            assert instance["payload_key"] == payload_instance.payload_key
            assert instance["start_type"] == InstanceStartType.PAYLOAD.value
    assert len(Instance.select().where(Instance.payload_key.is_null(False))) == 1


@pytest.mark.integration
def test_search_instances(client, journey, instances, g_user):
    response = client.post(f"/observability/v1/projects/{journey.project.id}/instances/search", json={})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 6

    response = client.post(f"/observability/v1/projects/{journey.project.id}/instances/search", json={})
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 6

    response = client.post(
        f"/observability/v1/projects/{journey.project.id}/instances/search",
        json={"params": {"journey_id": [str(uuid4())]}},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0

    response = client.post(
        f"/observability/v1/projects/{journey.project.id}/instances/search", json={"params": {"active": "false"}}
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0

    response = client.post(
        f"/observability/v1/projects/{journey.project.id}/instances/search",
        json={"params": {"start_range_end": datetime.now(timezone.utc).isoformat()}},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 6

    response = client.post(
        f"/observability/v1/projects/{journey.project.id}/instances/search",
        json={"params": {"journey_id": [instances[0].journey_id]}},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 6

    response = client.post(
        f"/observability/v1/projects/{journey.project.id}/instances/search", json={"params": {"page": 2}}
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 0

    response = client.post(
        f"/observability/v1/projects/{journey.project.id}/instances/search",
        json={"params": {"sort": SortOrder.ASC.name}},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 6


@pytest.mark.integration
def test_list_instances_plain_forbidden(client, journey, g_user_2):
    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_instances_with_runs(client, journey, instance, instance_runs, run_alerts, g_user):
    # request with pagination to ensure prefetches are not limited nor limiting the results
    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances?count=2")
    assert response.status_code == HTTPStatus.OK, response.json

    assert response.json["total"] == 1
    assert len(response.json["entities"]) == 1
    instance = response.json["entities"][0]
    assert instance["journey"]["id"] == str(journey.id)
    assert instance["journey"]["name"] == journey.name
    assert instance["start_time"] is not None
    assert instance["end_time"] is None
    assert instance["active"] is True
    assert instance["runs_summary"] == [{"status": instance_runs[0].status, "count": len(instance_runs)}]
    assert sum(al["count"] for al in instance["alerts_summary"]) == len(run_alerts)
    assert instance["alerts_summary"][0]["description"] == "Alert for run 1"
    assert instance["tests_summary"] == []


@pytest.mark.integration
def test_list_instances_with_tests(client, journey, instance, instance_runs, test_outcomes, g_user):
    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances")
    assert response.status_code == HTTPStatus.OK, response.json

    assert response.json["total"] == 1
    assert len(response.json["entities"]) == 1
    instance = response.json["entities"][0]
    assert instance["journey"]["id"] == str(journey.id)
    assert instance["journey"]["name"] == journey.name
    assert instance["start_time"] is not None
    assert instance["end_time"] is None
    assert instance["active"] is True
    assert instance["runs_summary"] == [{"status": instance_runs[0].status, "count": len(instance_runs)}]
    assert instance["tests_summary"] == [{"status": "FAILED", "count": 1}, {"status": "PASSED", "count": 1}]


@pytest.mark.integration
def test_list_instances_with_multiple_instances(client, journey, instance, instance_runs, test_outcomes, g_user):
    journey2 = Journey.create(name="J2", project=journey.project.id)
    instance2 = Instance.create(journey=journey2.id)

    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 2
    assert len(response.json["entities"]) == 2

    data = sorted(response.json["entities"], key=lambda x: x["journey"]["name"])

    assert data[0]["journey"]["id"] == str(journey.id)
    assert data[0]["project"]["id"] == str(journey.project.id)
    assert data[0]["project"]["name"] == journey.project.name
    assert data[0]["id"] == str(instance.id)
    assert data[0]["runs_summary"] == [{"status": instance_runs[0].status, "count": len(instance_runs)}]
    assert data[0]["tests_summary"] == [{"status": "FAILED", "count": 1}, {"status": "PASSED", "count": 1}]

    assert data[1]["journey"]["id"] == str(journey2.id)
    assert data[1]["project"]["id"] == str(journey.project.id)
    assert data[1]["project"]["name"] == journey.project.name
    assert data[1]["id"] == str(instance2.id)
    assert data[1]["runs_summary"] == []
    assert data[1]["tests_summary"] == []


@pytest.mark.integration
def test_list_instances_no_param_results(client, journey, instances, instance_runs, g_user):
    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances?journey_id={uuid4()}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0


@dataclass
class InstanceData:
    company: Company
    organization: Organization
    project: Project
    journey: Journey
    instances: list[Instance] = field(default_factory=list)


def create_instance_data(number: int, proj: Optional[Project] = None) -> InstanceData:
    c = Company.create(name=f"TestCompany{number}")
    org = Organization.create(name=f"Internal Org{number}", company=c)
    if proj:
        project = proj
    else:
        project = Project.create(name=f"Test_Project{number}", organization=org)
    journey = Journey.create(name=f"Test_Journey{number}", project=project)

    instance = InstanceData(c, org, project, journey)
    for _ in range(3):
        i = Instance.create(journey=journey)
        instance.instances.append(i)
    return instance


@pytest.mark.integration
def test_list_instances_with_param_results(client, journey, instances, g_user, project):
    instance_data1 = create_instance_data(1, proj=project)
    instance_data2 = create_instance_data(2, proj=project)
    create_instance_data(3, proj=project)

    # With only one journey_id there should be 3 total runs returned
    r1 = client.get(
        f"/observability/v1/projects/{instance_data1.project.id}/instances?journey_id={instance_data1.journey.id}"
    )
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 3

    # With both, there should be 6
    r2 = client.get(
        f"/observability/v1/projects/{instance_data1.project.id}/instances?journey_id={instance_data1.journey.id}&journey_id={instance_data2.journey.id}"
    )
    assert r2.status_code == HTTPStatus.OK, r2.json
    assert r2.json["total"] == 6


@pytest.mark.integration
def test_list_instances_with_filters_param_results(client, journey, g_user, project):
    instance_data1 = create_instance_data(1, proj=project)
    create_instance_data(2, proj=project)
    create_instance_data(3, proj=project)
    for instance in instance_data1.instances:
        instance.end_time = datetime.utcnow()
        instance.save()

    args = [("journey_name", name) for name in ("Test_Journey1", "Test_Journey2")] + [
        ("start_range_begin", (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()),
        ("start_range_end", datetime.now(timezone.utc).isoformat()),
    ]
    query_string = MultiDict(args)

    r1 = client.get(f"/observability/v1/projects/{instance_data1.project.id}/instances", query_string=query_string)
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 6

    r1 = client.get(
        f"/observability/v1/projects/{instance_data1.project.id}/instances", query_string=MultiDict([("active", True)])
    )
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 6
    r1 = client.get(
        f"/observability/v1/projects/{instance_data1.project.id}/instances", query_string=MultiDict([("active", False)])
    )
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 3
    r1 = client.get(
        f"/observability/v1/projects/{instance_data1.project.id}/instances",
        query_string=MultiDict([("start_range_begin", datetime.now(timezone.utc).isoformat())]),
    )
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 0


@pytest.mark.integration
def test_list_instances_with_invalid_date_filter(client, journey, g_user, project):
    args = [
        ("start_range_begin", "invalid date"),
    ]
    query_string = MultiDict(args)
    response = client.get(f"/observability/v1/projects/{project.id}/instances", query_string=query_string)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_list_instances_with_pagination(client, journey, instances, g_user):
    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances")
    assert response.status_code == HTTPStatus.OK, response.json
    full_result = response.json

    response = client.get(f"/observability/v1/projects/{journey.project.id}/instances?count=2&page=3")
    assert response.status_code == HTTPStatus.OK, response.json
    page_result = response.json

    assert full_result["total"] == 6
    assert page_result["total"] == 6
    assert len(full_result["entities"]) == 6
    assert len(page_result["entities"]) == 2


@pytest.mark.integration
def test_list_instances_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid4()}/instances")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_instances_forbidden(client, project):
    response = client.get(f"/observability/v1/projects/{project.id}/instances")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_instance(
    client, g_user, instance, run_alerts, instance_alert, instance_alerts_components, pipeline, pipeline_2
):
    response = client.get(f"/observability/v1/instances/{instance.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    resp = response.json
    assert resp["id"] == str(instance.id)
    assert resp["project"] == {"id": str(instance.journey.project_id), "name": instance.journey.project.name}
    assert resp["active"] == instance.active
    assert resp["end_time"] == (None if not instance.end_time else instance.end_time.isoformat())
    assert resp["expected_end_time"] is None  # No instance schedules configured -> no expected end times
    assert resp["start_time"] == instance.start_time.isoformat()
    assert resp["runs_summary"] == [{"count": 6, "status": "COMPLETED"}]
    assert resp["tests_summary"] == []
    assert len(resp["alerts_summary"]) == 12, resp["alerts_summary"]
    assert sum(al["count"] for al in resp["alerts_summary"]) == 13
    assert resp["alerts_summary"][0]["description"] == "Alert for run 1"
    assert resp["alerts_summary"][-2] == {"count": 2, "description": "Additional Errors (ct)", "level": "ERROR"}
    assert resp["alerts_summary"][-1] == {"count": 1, "description": "Additional Warnings (ct)", "level": "WARNING"}
    assert resp["payload_key"] is None


@pytest.mark.integration
def test_get_instance_forbidden(client, g_user_2, instance, run_alerts):
    response = client.get(f"/observability/v1/instances/{instance.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_instance_many_runs(client, g_user, instance, instance_runs, test_outcomes):
    response = client.get(f"/observability/v1/instances/{instance.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    resp = response.json
    assert resp["id"] == str(instance.id)
    assert resp["project"] == {"id": str(instance.journey.project_id), "name": instance.journey.project.name}
    assert resp["journey"] == {"name": instance.journey.name, "id": str(instance.journey.id)}
    assert resp["active"] == instance.active
    assert resp["end_time"] == (None if not instance.end_time else instance.end_time.isoformat())
    assert resp["start_time"] == instance.start_time.isoformat()
    assert resp["runs_summary"] == [{"status": instance_runs[0].status, "count": len(instance_runs)}]
    assert len(resp["alerts_summary"]) == 6
    assert resp["tests_summary"] == [{"count": 1, "status": "FAILED"}, {"count": 1, "status": "PASSED"}]


@pytest.mark.integration
def test_get_instance_different_runs_status(client, g_user, instance, instance_runs_different_statuses):
    run = instance_runs_different_statuses[0]
    TestOutcome.create(
        component=run.pipeline, name="Foo", status=TestStatuses.WARNING.name, run=run, instance_set=run.instance_set_id
    )
    response = client.get(f"/observability/v1/instances/{instance.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json == {
        "id": str(instance.id),
        "project": {"id": str(instance.journey.project_id), "name": instance.journey.project.name},
        "journey": {"name": instance.journey.name, "id": str(instance.journey.id)},
        "active": instance.active,
        "end_time": None if not instance.end_time else instance.end_time.isoformat(),
        "expected_end_time": None,  # No instance schedules configured -> no expected end times
        "start_time": instance.start_time.isoformat(),
        "runs_summary": [
            {"status": "COMPLETED", "count": 3},
            {"status": "COMPLETED_WITH_WARNINGS", "count": 1},
            {"status": "RUNNING", "count": 2},
        ],
        "alerts_summary": [],
        "tests_summary": [{"count": 1, "status": "WARNING"}],
        "status": InstanceStatus.ACTIVE.value,
        "payload_key": None,
        "start_type": InstanceStartType.DEFAULT.value,
    }


@pytest.mark.integration
def test_get_instances_not_found(client, g_user, instance):
    response = client.get(f"/observability/v1/instances/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_get_instances_forbidden(client, instances):
    response = client.get(f"/observability/v1/instances/{instances[0].id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_instance_with_expected_end_time(client, g_user, instance, instance_rule_end):
    response = client.get(f"/observability/v1/instances/{instance.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    resp = response.json
    assert resp["id"] == str(instance.id)
    assert resp["end_time"] is None
    assert resp["expected_end_time"] is not None


@pytest.mark.integration
@pytest.mark.parametrize(
    "num_instances, instance_alert_ct, run_alert_ct",
    [
        (1, AlertCount(error_ct=1, warning_ct=0), AlertCount(error_ct=2, warning_ct=0)),
        (2, AlertCount(error_ct=1, warning_ct=0), AlertCount(error_ct=2, warning_ct=0)),
        (1, AlertCount(error_ct=10, warning_ct=1), AlertCount(error_ct=7, warning_ct=7)),
        (2, AlertCount(error_ct=10, warning_ct=1), AlertCount(error_ct=7, warning_ct=7)),
    ],
    ids=[
        "single instance",
        "multiple instances",
        "single instance additional alerts",
        "multiple instances additional alerts",
    ],
)
def test_list_company_instances(num_instances, instance_alert_ct, run_alert_ct, client, g_user, organization, instance):
    context = TestProjectContext(
        org=organization,
        num_instances=num_instances,
        instance_alert_ct=instance_alert_ct,
        run_alert_ct=run_alert_ct,
    )
    response = client.get("/observability/v1/instances", query_string=MultiDict([("project_id", context.project.id)]))
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == len(context.instances)
    for resp, expected in zip(data["entities"], context.instances):
        assert resp["id"] == str(expected.id)
        assert resp["project"] == {"id": str(expected.journey.project_id), "name": expected.journey.project.name}
        assert resp["active"] == expected.active
        assert resp["end_time"] == (None if not expected.end_time else expected.end_time.isoformat())
        assert resp["start_time"] == expected.start_time.isoformat()
        total_instance_alerts = instance_alert_ct.error_ct + instance_alert_ct.warning_ct
        total_run_alerts = run_alert_ct.error_ct + run_alert_ct.warning_ct
        assert sum(al["count"] for al in resp["alerts_summary"]) == total_instance_alerts + total_run_alerts
        assert resp["tests_summary"] == []
        assert resp["payload_key"] is None


@pytest.mark.integration
def test_list_company_instances_alerts_summary_payload(client, g_user, organization):
    context = TestProjectContext(
        org=organization,
        num_instances=1,
        instance_alert_ct=AlertCount(error_ct=10, warning_ct=1),
        run_alert_ct=AlertCount(error_ct=10, warning_ct=9),
    )
    RunAlert.update({RunAlert.description: "warning text"}).where(RunAlert.level == AlertLevel.WARNING).execute()
    RunAlert.update({RunAlert.description: "error text"}).where(RunAlert.level == AlertLevel.ERROR).execute()
    response = client.get("/observability/v1/instances", query_string=MultiDict([("project_id", context.project.id)]))
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == len(context.instances)
    alerts_summary = response.json["entities"][0]["alerts_summary"]
    assert len(alerts_summary) == 12
    assert sum(al["count"] for al in alerts_summary) == 30
    # Top 2 count
    assert alerts_summary[0] == {"count": 10, "description": "error text", "level": "ERROR"}
    assert alerts_summary[1] == {"count": 9, "description": "warning text", "level": "WARNING"}
    # Additional alerts by level
    assert alerts_summary[-2] == {
        "count": 2,
        "description": ADDITIONAL_ALERT_DESCRIPTION[AlertLevel.ERROR.value],
        "level": "ERROR",
    }
    assert alerts_summary[-1] == {
        "count": 1,
        "description": ADDITIONAL_ALERT_DESCRIPTION[AlertLevel.WARNING.value],
        "level": "WARNING",
    }


@pytest.mark.integration
def test_list_company_instances_project_filter(client, g_user, organization):
    p1 = TestProjectContext(org=organization, name="test_project_filter_1")
    p2 = TestProjectContext(org=organization, name="test_project_filter_2")

    # Default select all projects in the company
    response = client.get("/observability/v1/instances")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 2
    for data, expected in zip(response.json["entities"], [p1, p2]):
        assert data["project"] == {"id": str(expected.project.id), "name": expected.project.name}

    response = client.get(
        "/observability/v1/instances",
        query_string=MultiDict([("project_id", p1.project.id)]),
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 1
    assert response.json["entities"][0]["project"] == {"id": str(p1.project.id), "name": p1.project.name}


@pytest.mark.integration
def test_list_company_instances_filter_project_outside_company(client, g_user, organization_2):
    context = TestProjectContext(org=organization_2, name="test_project_filter_org2")

    assert context.project.organization.company.id != g_user.primary_company.id
    assert Instance.select().join(Journey).join(Project).where(Project.id == context.project.id).count() == 1

    response = client.get("/observability/v1/instances", query_string=MultiDict([("project_id", context.project.id)]))
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 0


@pytest.mark.integration
def test_list_company_instances_forbidden(client, project):
    response = client.get("/observability/v1/instances")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_instances_status_filter(client, journey, g_user, project):
    active_instance = Instance.create(journey=journey)
    completed_instance = Instance.create(journey=journey, end_time=datetime.utcnow())
    error_instance = Instance.create(journey=journey, has_errors=True)
    warning_instance = Instance.create(journey=journey, has_warnings=True)

    for status, instance in zip(
        [InstanceStatus.ACTIVE, InstanceStatus.COMPLETED, InstanceStatus.ERROR, InstanceStatus.WARNING],
        [active_instance, completed_instance, error_instance, warning_instance],
    ):
        res = client.get(
            f"/observability/v1/projects/{project.id}/instances", query_string=MultiDict([("status", status.value)])
        )
        assert res.status_code == HTTPStatus.OK, res.json
        assert res.json["total"] == 1
        data = res.json["entities"][0]
        assert data["id"] == str(instance.id)
        assert data["status"] == status.value

    # Filter multiple statuses
    res = client.get(
        f"/observability/v1/projects/{project.id}/instances",
        query_string=MultiDict([("status", status.value) for status in InstanceStatus]),
    )
    assert res.status_code == HTTPStatus.OK, res.json
    assert res.json["total"] == 4


@pytest.mark.integration
def test_list_company_instances_status_filter(client, journey, g_user, project):
    active_instance = Instance.create(journey=journey)
    completed_instance = Instance.create(journey=journey, end_time=datetime.utcnow())
    error_instance = Instance.create(journey=journey, has_errors=True)
    warning_instance = Instance.create(journey=journey, has_warnings=True)

    for status, instance in zip(
        [InstanceStatus.ACTIVE, InstanceStatus.COMPLETED, InstanceStatus.ERROR, InstanceStatus.WARNING],
        [active_instance, completed_instance, error_instance, warning_instance],
    ):
        res = client.get("/observability/v1/instances", query_string=MultiDict([("status", status.value)]))
        assert res.status_code == HTTPStatus.OK, res.json
        assert res.json["total"] == 1
        data = res.json["entities"][0]
        assert data["id"] == str(instance.id)
        assert data["status"] == status.value

    # Filter multiple statuses
    res = client.get(
        "/observability/v1/instances", query_string=MultiDict([("status", status.value) for status in InstanceStatus])
    )
    assert res.status_code == HTTPStatus.OK, res.json
    assert res.json["total"] == 4

    # None status -> n/a
    res = client.get("/observability/v1/instances", query_string=MultiDict([("status", None)]))
    assert res.status_code == HTTPStatus.OK, res.json
    assert res.json["total"] == 4


@pytest.mark.integration
@pytest.mark.parametrize(
    "company_endpoint",
    (
        True,
        False,
    ),
)
def test_list_company_instances_expected_end_time(
    client, journey, g_user, project, instance_rule_start, company_endpoint
):
    active_instance = Instance.create(journey=journey)
    inactive_instance = Instance.create(journey=journey, end_time=datetime.utcnow())

    if company_endpoint:
        response = client.get("/observability/v1/instances")
    else:
        response = client.get(f"/observability/v1/projects/{project.id}/instances")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 2
    assert response.json["entities"][0]["id"] == str(active_instance.id)
    assert response.json["entities"][0]["end_time"] is None
    assert response.json["entities"][0]["expected_end_time"] is not None
    assert response.json["entities"][1]["id"] == str(inactive_instance.id)
    assert response.json["entities"][1]["end_time"] is not None
    assert response.json["entities"][1]["expected_end_time"] is None


@pytest.mark.integration
def test_get_instance_dag(client, g_user, organization):
    context = TestProjectContext(org=organization, name="test_instance_dag")
    instance = context.instances[0]

    response = client.get(f"/observability/v1/instances/{instance.id}/dag")

    assert response.status_code == HTTPStatus.OK, response.json
    assert "nodes" in response.json and isinstance(response.json["nodes"], list)
    assert sorted([n["component"]["id"] for n in response.json["nodes"]]) == sorted(
        [str(n.id) for n in instance.dag_nodes]
    )

    pipeline_node = [n for n in response.json["nodes"] if n["component"]["id"] == str(context.pipeline.id)][0]
    assert pipeline_node["alerts_summary"] and pipeline_node["alerts_summary"][0]["level"] == "ERROR"
    assert pipeline_node["runs_summary"] and pipeline_node["runs_summary"][0]["status"] == "RUNNING"
    assert pipeline_node["tests_summary"] and pipeline_node["tests_summary"][0]["status"] == "FAILED"

    dataset_node = [n for n in response.json["nodes"] if n["component"]["id"] == str(context.dataset.id)][0]
    assert (
        dataset_node["operations_summary"]
        and dataset_node["operations_summary"][1]["operation"] == "WRITE"
        and dataset_node["operations_summary"][1]["count"] == 1
    )

    assert pipeline_node["status"] == RunStatus.FAILED.name
    assert dataset_node["status"] == RunStatus.COMPLETED.name
