from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from http import HTTPStatus
from itertools import chain
from typing import Optional
from uuid import UUID, uuid4

import pytest
from werkzeug.datastructures import MultiDict

from common.entities import (
    AlertLevel,
    Company,
    Instance,
    InstanceSet,
    Organization,
    Pipeline,
    Project,
    Run,
    RunAlert,
    RunAlertType,
    RunStatus,
    RunTask,
    RunTaskStatus,
    Task,
    TestOutcome,
)
from common.events.enums import EventSources
from common.events.v1 import ApiRunStatus, RunStatusEvent, RunStatusSchema, TestStatuses


@pytest.fixture
def instances(client, journey, runs):
    for r in runs:
        instance = Instance.create(journey=journey)
        instance_set = InstanceSet.get_or_create([instance.id])
        r.instance_set = instance_set
        r.save()
    results = Instance.select().where(Instance.journey == journey)
    yield results


@pytest.fixture
def run_tasks(runs, tasks):
    for run in runs:
        RunTask.create(run=run, task=tasks[0], start_time=datetime.now(), status=RunTaskStatus.COMPLETED.name)
        RunTask.create(run=run, task=tasks[1], start_time=datetime.now(), status=RunTaskStatus.FAILED.name)
        RunTask.create(run=run, task=tasks[2], start_time=datetime.now(), status=RunTaskStatus.FAILED.name)
    results = RunTask.select().where(RunTask.run.in_(runs))
    yield results


@pytest.fixture
def uuid_value():
    return uuid4()


@pytest.fixture
def run_status_event(runs, pipeline, project, uuid_value):
    ts = str(datetime.now(UTC))
    yield RunStatusEvent(
        **RunStatusSchema().load(
            {
                "project_id": project.id,
                "event_id": uuid_value,
                "pipeline_id": pipeline.id,
                "run_key": "run-correlation",
                "run_id": runs[0].id,
                "task_key": "task_key",
                "task_id": UUID("185208fd-1062-4f4a-a59f-61f2db99c3d7"),
                "task_name": "My Task",
                "source": EventSources.API.name,
                "pipeline_key": "4da46ac7-c318-4cbd-83bb-83edaa6044c5",
                "pipeline_name": "My Pipeline",
                "received_timestamp": ts,
                "event_timestamp": ts,
                "external_url": "https://example.com",
                "run_task_id": UUID("c3fc7f3d-c3b1-4d08-8e98-439bc4918ce6"),
                "metadata": {"key": "value"},
                "event_type": RunStatusEvent.__name__,
                "status": ApiRunStatus.RUNNING.name,
            }
        )
    )


@pytest.mark.integration
def test_list_runs(client, g_user, pipeline, runs, tasks):
    for run in runs:
        RunTask.create(run=run, task=tasks[0], start_time=datetime.now(), status=RunTaskStatus.COMPLETED.name)
        RunTask.create(run=run, task=tasks[1], start_time=datetime.now(), status=RunTaskStatus.FAILED.name)
        RunTask.create(run=run, task=tasks[2], start_time=datetime.now(), status=RunTaskStatus.FAILED.name)
        TestOutcome.create(
            component=pipeline,
            run=run,
            task=tasks[0],
            name=f"TO-{run.id}-{tasks[0].id}",
            status=TestStatuses.PASSED.name,
            instance_set=run.instance_set,
        )
        TestOutcome.create(
            component=pipeline,
            run=run,
            task=tasks[1],
            name=f"TO-{run.id}-{tasks[1].id}",
            status=TestStatuses.FAILED.name,
            instance_set=run.instance_set,
        )
        TestOutcome.create(
            component=pipeline,
            run=run,
            task=tasks[2],
            name=f"TO-{run.id}-{tasks[2].id}",
            status=TestStatuses.FAILED.name,
            instance_set=run.instance_set,
        )
    response = client.get(f"/observability/v1/projects/{pipeline.project.id}/runs")
    assert response.status_code == HTTPStatus.OK, response.json

    expected_total = len(runs)
    found_total = response.json["total"]

    statuses = (
        (RunTaskStatus.PENDING, 0),
        (RunTaskStatus.MISSING, 0),
        (RunTaskStatus.RUNNING, 0),
        (RunTaskStatus.COMPLETED, 1),
        (RunTaskStatus.COMPLETED_WITH_WARNINGS, 0),
        (RunTaskStatus.FAILED, 2),
    )
    expected_tests = (
        (TestStatuses.FAILED, 2),
        (TestStatuses.PASSED, 1),
    )
    keys = ("1", "2", "3", "4", "5", "6")
    assert expected_total == found_total, f"Got {found_total} runs but expected {expected_total}"
    for run in response.json["entities"]:
        assert len(run["pipeline"]) == 4
        assert run["pipeline"]["key"] == pipeline.key
        assert run["pipeline"]["display_name"] == pipeline.display_name
        assert run["pipeline"]["tool"] == pipeline.tool
        assert run["status"] == "COMPLETED"
        assert run["pipeline"]["id"] == str(pipeline.id)
        assert run["key"] in keys, f"Unexpected run key: {run['key']}"
        assert run["name"] in (f"name{k}" for k in keys), f"Unexpected run key: {run['key']}"
        assert len(run["tasks_summary"]) == len(statuses)
        assert len(run["alerts"]) == 1
        assert run["alerts"][0]["run"] == run["id"]

        for (_, expected), actual in zip(
            sorted(statuses, key=lambda x: x[0].name), sorted(run["tasks_summary"], key=lambda x: x["status"])
        ):
            assert expected == actual["count"]
        assert len(run["tests_summary"]) == len(expected_tests)
        for (outcome, expected), actual in zip(
            sorted(expected_tests, key=lambda x: x[0].name), sorted(run["tests_summary"], key=lambda x: x["status"])
        ):
            assert (outcome.name, expected) == (actual["status"], actual["count"])


@pytest.mark.integration
def test_list_runs_forbidden(client, g_user_2, project):
    response = client.get(f"/observability/v1/projects/{project.id}/runs")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_runs_no_param_results(client, g_user, pipeline, runs):
    response = client.get(f"/observability/v1/projects/{pipeline.project.id}/runs?pipeline_id={uuid4()}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0


@dataclass
class RunData:
    company: Company
    organization: Organization
    project: Project
    pipeline: Pipeline
    runs: list[Run] = field(default_factory=list)
    alerts: list[RunAlert] = field(default_factory=list)


def create_run_data(number: int, proj: Project | None = None, set_tool=False) -> RunData:
    c = Company.create(name=f"TestCompany{number}")
    org = Organization.create(name=f"Internal Org{number}", company=c)
    if proj:
        project = proj
    else:
        project = Project.create(name=f"Test_Project{number}", organization=org)
    pipe = Pipeline.create(key=f"Test_Pipeline{number}", project=project, tool=f"TOOL_{number}" if set_tool else None)
    run = RunData(c, org, project, pipe)
    for key, status in enumerate(
        (RunStatus.RUNNING.name, RunStatus.COMPLETED.name, RunStatus.COMPLETED_WITH_WARNINGS.name)
    ):
        r = Run.create(key=str(key), pipeline=pipe, status=status)
        run.runs.append(r)
        run_alert = RunAlert.create(
            run=r,
            description=f"Alert for run {key}",
            name=f"key {key}",
            level=AlertLevel["WARNING"].value,
            type=RunAlertType["LATE_START"].value,
        )
        run.alerts.append(run_alert)
    return run


@pytest.mark.integration
def test_list_runs_with_param_results(client, g_user_2_admin, pipeline, runs):
    rd_one = create_run_data(1)
    rd_two = create_run_data(2, proj=rd_one.project)
    _ = create_run_data(3, proj=rd_two.project)

    # With only one pipeline_id there should be 3 total runs returned
    r1 = client.get(f"/observability/v1/projects/{rd_one.project.id}/runs?pipeline_id={rd_one.pipeline.id}")
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 3

    # With both, there should be 6
    r2 = client.get(
        f"/observability/v1/projects/{rd_one.project.id}/runs?pipeline_id={rd_one.pipeline.id}&pipeline_id={rd_two.pipeline.id}"
    )
    assert r2.status_code == HTTPStatus.OK, r2.json
    assert r2.json["total"] == 6


@pytest.mark.integration
def test_list_runs_with_filters_param_results(client, g_user_2_admin, pipeline, runs):
    rd_one = create_run_data(1)
    rd_two = create_run_data(2, proj=rd_one.project)
    _ = create_run_data(3, proj=rd_two.project)

    args = (
        [("run_key", key) for key in ("1", "2")]
        + [("pipeline_key", key) for key in ("Test_Pipeline1", "Test_Pipeline2")]
        + [
            ("start_range_begin", (datetime.now(UTC) - timedelta(hours=1)).isoformat()),
            ("start_range_end", datetime.now(UTC).isoformat()),
        ]
    )
    query_string = MultiDict(args)

    r1 = client.get(f"/observability/v1/projects/{rd_one.project.id}/runs", query_string=query_string)
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 4


@pytest.mark.integration
def test_list_runs_with_status_filters(client, g_user, project):
    rd_one = create_run_data(1, proj=project)
    rd_two = create_run_data(2, proj=project)
    _ = create_run_data(3, proj=rd_two.project)

    qs = MultiDict(("status", status) for status in (RunStatus.COMPLETED.name, RunStatus.RUNNING.name))
    r2 = client.get(f"/observability/v1/projects/{rd_one.project.id}/runs")
    r1 = client.get(f"/observability/v1/projects/{rd_one.project.id}/runs", query_string=qs)
    unfiltered_body = r2.json
    filtered_body = r1.json
    assert r1.status_code == r2.status_code == HTTPStatus.OK, (unfiltered_body, filtered_body)
    assert unfiltered_body["total"] == 9
    assert filtered_body["total"] == 6
    assert all(e["status"] in (RunStatus.COMPLETED.name, RunStatus.RUNNING.name) for e in filtered_body["entities"])


@pytest.mark.integration
def test_list_runs_with_tool_filter(client, g_user, project):
    rd1 = create_run_data(1, proj=project, set_tool=True)
    rd2 = create_run_data(2, proj=project, set_tool=True)
    rd3 = create_run_data(3, proj=project, set_tool=True)

    response = client.get(f"/observability/v1/projects/{project.id}/runs")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 9

    qs = MultiDict([("tool", rd1.pipeline.tool)])
    response = client.get(f"/observability/v1/projects/{project.id}/runs", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 3
    assert {e["id"] for e in data["entities"]} == {str(r.id) for r in rd1.runs}

    qs = MultiDict([("tool", rd1.pipeline.tool.lower()), ("tool", rd3.pipeline.tool)])
    response = client.get(f"/observability/v1/projects/{project.id}/runs", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 6
    assert {e["id"] for e in data["entities"]} == {str(r.id) for r in chain(rd1.runs, rd3.runs)}


@pytest.mark.integration
def test_list_runs_with_pagination(client, g_user, pipeline, runs):
    full_result = client.get(f"/observability/v1/projects/{pipeline.project.id}/runs").json
    page_result = client.get(f"/observability/v1/projects/{pipeline.project.id}/runs?count=2&page=3").json

    assert full_result["total"] == 6
    assert page_result["total"] == 6
    assert len(page_result["entities"]) == 2
    assert full_result["entities"][4]["key"] == page_result["entities"][0]["key"]
    assert full_result["entities"][5]["key"] == page_result["entities"][1]["key"]


@pytest.mark.integration
def test_list_runs_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid4()}/runs")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_runs_with_instances_filter(project, runs, pipeline, instances, client, g_user):
    selected_instances = instances[:3]
    qs = MultiDict(("instance_id", str(i.id)) for i in selected_instances)
    expected_runs = [str(run.id) for inst in selected_instances for run in inst.iis[0].instance_set.runs]

    r1 = client.get(f"/observability/v1/projects/{project.id}/runs", query_string=qs)
    filtered_body = r1.json
    r2 = client.get(f"/observability/v1/projects/{project.id}/runs")
    unfiltered_body = r2.json

    assert r1.status_code == r2.status_code == HTTPStatus.OK, (unfiltered_body, filtered_body)
    assert unfiltered_body["total"] == 6
    assert filtered_body["total"] == len(expected_runs)
    assert [run["id"] for run in filtered_body["entities"]] == expected_runs


@pytest.mark.integration
def test_list_runs_with_search(client, g_user, project, runs):
    # Search matching key
    search_1 = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"search": "3"})
    assert search_1.status_code == HTTPStatus.OK, search_1.json
    data_1 = search_1.json
    assert data_1["total"] == 1
    assert len(data_1["entities"]) == 1

    # Search matching name (case-insensitive)
    search_2 = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"search": "NAME5"})
    assert search_2.status_code == HTTPStatus.OK, search_2.json
    data_2 = search_2.json
    assert data_2["total"] == 1
    assert len(data_2["entities"]) == 1

    # Partial Search
    search_3 = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"search": "me4"})
    assert search_3.status_code == HTTPStatus.OK, search_3.json
    data_3 = search_3.json
    assert data_3["total"] == 1
    assert len(data_3["entities"]) == 1

    # No matches
    search_4 = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"search": "qwerty"})
    assert search_4.status_code == HTTPStatus.OK, search_4.json
    data_4 = search_4.json
    assert data_4["total"] == 0
    assert len(data_4["entities"]) == 0


@pytest.mark.integration
def test_get_run_info(client, g_user, pipeline):
    # Create a run
    run = Run.create(key="some key", pipeline=pipeline, status=RunStatus.RUNNING.name)
    run_alert = RunAlert.create(
        run=run,
        description="Alert for run 0",
        name="key 0",
        level=AlertLevel["WARNING"].value,
        type=RunAlertType["LATE_START"].value,
    )

    def _add_run_tasks(status, count, test_status):
        for j in range(count):
            task = Task.create(key=f"test task{pipeline.id}-{status.name}-{j}", pipeline=pipeline)
            RunTask.create(run=run, task=task, start_time=datetime.now(), status=status.name)
            TestOutcome.create(
                component=pipeline,
                run=run,
                task=task,
                name=f"test test{pipeline.id}-{test_status.name}-{j}",
                status=test_status.name,
                instance_set=run.instance_set,
            )

    statuses = (
        (RunTaskStatus.PENDING, 0, TestStatuses.FAILED),
        (RunTaskStatus.MISSING, 1, TestStatuses.FAILED),
        (RunTaskStatus.RUNNING, 11, TestStatuses.PASSED),
        (RunTaskStatus.COMPLETED, 0, TestStatuses.PASSED),
        (RunTaskStatus.COMPLETED_WITH_WARNINGS, 3, TestStatuses.WARNING),
        (RunTaskStatus.FAILED, 0, TestStatuses.FAILED),
    )
    assert len(statuses) == len(RunTaskStatus)
    for status in statuses:
        _add_run_tasks(*status)

    # Make sure we can retrieve the run information
    response = client.get(f"/observability/v1/runs/{run.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json

    assert data["id"] == str(run.id), f"Expected id {run.id} but got {data.get('id')}"
    assert data["key"] == str(run.key), f"Expected key 'some key' but got {data.get('key')}"
    assert data["name"] is None
    assert len(data["alerts"]) == 1
    assert data["alerts"][0]["id"] == str(run_alert.id)
    assert data["pipeline"]["id"] == str(pipeline.id)
    assert data["pipeline"]["tool"] == pipeline.tool

    for (_, expected, _), actual in zip(
        sorted(statuses, key=lambda x: x[0].name), sorted(data["tasks_summary"], key=lambda x: x["status"])
    ):
        assert expected == actual["count"]

    # tests_summary don't include all statuses so filter out statuses that expect count=0
    for (_, expected, _), actual in zip(
        sorted(filter(lambda x: x[1] > 0, statuses), key=lambda x: x[2].name),
        sorted(data["tests_summary"], key=lambda x: x["status"]),
    ):
        assert expected == actual["count"]


@pytest.mark.integration
def test_get_run_info_forbidden(client, g_user_2, pipeline):
    run = Run.create(key="some key", pipeline=pipeline, status=RunStatus.RUNNING.name)
    response = client.get(f"/observability/v1/runs/{run.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_run_no_tasks(client, g_user, runs):
    response = client.get(f"/observability/v1/runs/{runs[0].id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "tasks_summary" in data
    assert len(data["tasks_summary"]) == len(RunTaskStatus)
    assert "name" in data["name"]
    for task_summary in data["tasks_summary"]:
        assert task_summary["count"] == 0
    assert "tests_summary" in data
    assert len(data["tests_summary"]) == 0


@pytest.mark.integration
def test_get_run_not_found(client, g_user, uuid_value):
    response = client.get(f"/observability/v1/runs/{uuid_value}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_batch_pipeline_runs(client, g_user, pipeline, runs, tasks, project):
    for run in runs:
        RunTask.create(run=run, task=tasks[0], start_time=datetime.now(), status=RunTaskStatus.COMPLETED.name)
        RunTask.create(run=run, task=tasks[1], start_time=datetime.now(), status=RunTaskStatus.FAILED.name)
        RunTask.create(run=run, task=tasks[2], start_time=datetime.now(), status=RunTaskStatus.FAILED.name)
        TestOutcome.create(
            component=pipeline,
            run=run,
            task=tasks[0],
            name=f"TO-{run.id}-{tasks[0].id}",
            status=TestStatuses.PASSED.name,
        )
        TestOutcome.create(
            component=pipeline,
            run=run,
            task=tasks[1],
            name=f"TO-{run.id}-{tasks[1].id}",
            status=TestStatuses.FAILED.name,
        )
        TestOutcome.create(
            component=pipeline,
            run=run,
            task=tasks[2],
            name=f"TO-{run.id}-{tasks[2].id}",
            status=TestStatuses.FAILED.name,
        )
    response = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"pipeline_id": pipeline.id})
    assert response.status_code == HTTPStatus.OK, response.json

    expected_total = len(runs)
    found_total = response.json["total"]

    statuses = (
        (RunTaskStatus.PENDING, 0),
        (RunTaskStatus.MISSING, 0),
        (RunTaskStatus.RUNNING, 0),
        (RunTaskStatus.COMPLETED, 1),
        (RunTaskStatus.COMPLETED_WITH_WARNINGS, 0),
        (RunTaskStatus.FAILED, 2),
    )
    expected_tests = (
        (TestStatuses.FAILED, 2),
        (TestStatuses.PASSED, 1),
    )
    assert expected_total == found_total, f"Got {found_total} runs but expected {expected_total}"
    for run in response.json["entities"]:
        assert len(run["pipeline"]) == 4
        assert run["pipeline"]["key"] == pipeline.key
        assert run["pipeline"]["display_name"] == pipeline.display_name
        assert run["pipeline"]["tool"] == pipeline.tool
        assert run["status"] == "COMPLETED"
        assert run["pipeline"]["id"] == str(pipeline.id)
        assert run["key"] in ("1", "2", "3", "4", "5", "6"), f"Unexpected run key: {run['key']}"
        assert len(run["tasks_summary"]) == len(statuses)
        assert len(run["alerts"]) == 1
        assert run["alerts"][0]["run"] == run["id"]

        for (_, expected), actual in zip(
            sorted(statuses, key=lambda x: x[0].name), sorted(run["tasks_summary"], key=lambda x: x["status"])
        ):
            assert expected == actual["count"]
        assert len(run["tests_summary"]) == len(expected_tests)
        for (outcome, expected), actual in zip(
            sorted(expected_tests, key=lambda x: x[0].name), sorted(run["tests_summary"], key=lambda x: x["status"])
        ):
            assert (outcome.name, expected) == (actual["status"], actual["count"])


@pytest.mark.integration
def test_list_batch_pipeline_runs_forbidden(client, g_user_2, pipeline, project):
    response = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"pipeline_id": pipeline.id})
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_batch_pipeline_runs_with_filters_param_results(client, g_user_2_admin, pipeline, runs, project):
    rd_one = create_run_data(1)
    rd_two = create_run_data(2, proj=rd_one.project)
    _ = create_run_data(3, proj=rd_two.project)

    args = [("run_key", key) for key in ("1", "2")] + [
        ("start_range_begin", (datetime.now(UTC) - timedelta(hours=1)).isoformat()),
        ("start_range_end", datetime.now(UTC).isoformat()),
        ("pipeline_id", pipeline.id),
    ]
    query_string = MultiDict(args)
    r1 = client.get(f"/observability/v1/projects/{project.id}/runs", query_string=query_string)
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 2

    r1 = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string=MultiDict(
            [
                ("start_range_begin", datetime.now(UTC).isoformat()),
                ("pipeline_id", pipeline.id),
            ]
        ),
    )
    assert r1.status_code == HTTPStatus.OK, r1.json
    assert r1.json["total"] == 0


@pytest.mark.integration
def test_list_batch_pipeline_runs_with_pagination(client, g_user, pipeline, runs, project):
    full_result = client.get(
        f"/observability/v1/projects/{project.id}/runs", query_string={"pipeline_id": pipeline.id}
    ).json
    page_result = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={"pipeline_id": pipeline.id, "count": 2, "page": 3},
    ).json

    assert full_result["total"] == 6
    assert page_result["total"] == 6
    assert len(page_result["entities"]) == 2
    assert full_result["entities"][4]["key"] == page_result["entities"][0]["key"]
    assert full_result["entities"][5]["key"] == page_result["entities"][1]["key"]


@pytest.mark.integration
def test_list_batch_pipeline_runs_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid4()}/runs")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_runs_for_instance(client, g_user, instances, runs, project):
    response = client.get(
        f"/observability/v1/projects/{project.id}/runs", query_string={"instance_id": [instances[0].id]}
    )
    assert response.status_code == HTTPStatus.OK, response.json
    response_body = response.json
    assert response_body["total"] == 1 and len(response_body["entities"]) == response_body["total"], (
        "should return one run for each instance"
    )
    assert len(response_body["entities"][0]["alerts"]) == 1
    expected_run_ids = [str(r.id) for r in runs]
    assert response_body["entities"][0]["id"] in expected_run_ids, "the returned ID isn't one of the expected runs"
    assert all(alert["run"] in expected_run_ids for alert in response_body["entities"][0]["alerts"])


@pytest.mark.integration
def test_list_runs_for_instance_forbidden(client, g_user_2, instances, runs, project):
    response = client.get(
        f"/observability/v1/projects/{project.id}/runs", query_string={"instance_id": [instances[0].id]}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_runs_for_instance_with_summaries(client, g_user, instances, runs, run_tests, run_tasks, project):
    response = client.get(
        f"/observability/v1/projects/{project.id}/runs", query_string={"instance_id": [instances[0].id]}
    )

    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1, "should return one run for each instance"
    run = response.json["entities"][0]
    assert any(run["id"] == str(r.id) for r in runs), "the returned ID isn't one of the expected runs"

    assert len(run["tests_summary"]) == 1
    assert run["tests_summary"][0] == {"count": 1, "status": TestStatuses.PASSED.name}

    assert len(run["tasks_summary"]) == len(RunTaskStatus.as_set())
    tasks_statuses = (
        (RunTaskStatus.PENDING, 0),
        (RunTaskStatus.MISSING, 0),
        (RunTaskStatus.RUNNING, 0),
        (RunTaskStatus.COMPLETED, 1),
        (RunTaskStatus.COMPLETED_WITH_WARNINGS, 0),
        (RunTaskStatus.FAILED, 2),
    )
    for status, expected in tasks_statuses:
        assert any((status.name, expected) == (task["status"], task["count"]) for task in run["tasks_summary"]), (
            f'did not find expected {{"status": {status.name}, "count": {expected}}} in {run["tasks_summary"]}'
        )

    assert len(run["alerts"]) == 1
    assert run["alerts"][0]["level"] == AlertLevel["ERROR"].value
    assert run["alerts"][0]["type"] == RunAlertType["LATE_START"].value


@pytest.mark.integration
def test_list_runs_for_instance_search_key(client, g_user, instances, project):
    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={"instance_id": [instances[0].id], "run_key": instances[0].iis[0].instance_set.runs[0].key},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 1, "should return one run for this key"

    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={"instance_id": [instances[0].id], "run_key": "qwerty"},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0, "should not return one run for this key"


@pytest.mark.integration
def test_list_runs_for_instance_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid4()}/runs")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_runs_for_instance_pagination(client, g_user, journey, runs, instance_instance_set, project):
    instance = Instance.create(journey=journey)
    instance_set = InstanceSet.get_or_create([instance.id])
    Run.update({"instance_set": instance_set}).where(Run.id << runs).execute()

    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={"instance_id": [instance.id], "count": 2, "page": 2},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 6
    assert len(response.json["entities"]) == 2
    assert response.json["entities"][0]["key"] == "3"
    assert response.json["entities"][1]["key"] == "4"


@pytest.mark.integration
def test_list_runs_for_instance_sort(client, g_user, journey, pipeline, runs, project):
    instance = Instance.create(journey=journey)
    instance_set = InstanceSet.get_or_create([instance.id])
    Run.create(key="r1", pipeline=pipeline, instance_set=instance_set, status="COMPLETED", start_time=datetime.now())
    Run.create(
        key="r2",
        pipeline=pipeline,
        instance_set=instance_set,
        status="COMPLETED",
        start_time=datetime.now() - timedelta(days=2),
    )
    Run.create(
        key="r3",
        pipeline=pipeline,
        instance_set=instance_set,
        status="COMPLETED",
        start_time=datetime.now() - timedelta(days=3),
    )

    # Sort by Run start_time ASC by default
    response = client.get(
        f"/observability/v1/projects/{project.id}/runs", query_string={"instance_id": [instance.id], "search": "r"}
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 3
    assert [d["key"] for d in response.json["entities"]] == ["r3", "r2", "r1"]

    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={"instance_id": [instance.id], "search": "r", "sort": "desc"},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 3
    assert [d["key"] for d in response.json["entities"]] == ["r1", "r2", "r3"]


@pytest.mark.integration
@pytest.mark.parametrize(
    "query_string, expected",
    [
        (RunStatus.COMPLETED.name, 3),
        ((RunStatus.FAILED.name, RunStatus.COMPLETED.name), 6),
        (RunStatus.COMPLETED_WITH_WARNINGS.name, 0),
    ],
)
def test_get_instance_runs_status_filters(query_string, expected, client, g_user, instance, pipeline, project):
    instance_set = InstanceSet.get_or_create([instance.id])
    for key in ("1", "2", "3", "4", "5", "6"):
        Run.create(
            key=key,
            pipeline=pipeline,
            instance_set=instance_set,
            status=f"{RunStatus.COMPLETED.name if int(key) % 2 == 0 else RunStatus.FAILED.name}",
        )
    base_query_string = {"instance_id": [instance.id], "status": query_string}
    response = client.get(f"/observability/v1/projects/{project.id}/runs", query_string=base_query_string)
    assert response.status_code == HTTPStatus.OK
    assert response.json["total"] == expected


@pytest.mark.integration
def test_get_instance_runs_component_id_filters(client, g_user, instance, instance_runs, project):
    pipeline2 = Pipeline.create(key="pipe2", project=project.id)
    instance_set = InstanceSet.get_or_create([instance.id])
    Run.create(key="run2", pipeline=pipeline2.id, status=RunStatus.RUNNING.name, instance_set=instance_set)

    # Base case: no filters
    response = client.get(f"/observability/v1/projects/{project.id}/runs", query_string={"instance_id": [instance.id]})
    assert response.status_code == HTTPStatus.OK
    assert response.json["total"] == 7

    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={"instance_id": [instance.id], "component_id": pipeline2.id},
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.integration
def test_get_instance_runs_date_filters(client, g_user, instance, instance_runs, project):
    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={
            "start_range_begin": datetime.now() - timedelta(days=1),
            "start_range_end": datetime.now() + timedelta(days=1),
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json["total"] == 6

    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={
            "start_range_begin": datetime.now() + timedelta(days=1),
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json["total"] == 0

    response = client.get(
        f"/observability/v1/projects/{project.id}/runs",
        query_string={
            "end_range_begin": datetime.now() + timedelta(days=1),
            "end_range_end": datetime.now() - timedelta(days=1),
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
