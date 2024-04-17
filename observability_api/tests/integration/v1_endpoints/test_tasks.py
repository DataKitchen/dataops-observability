from datetime import datetime, timedelta
from http import HTTPStatus
from uuid import uuid4

import pytest

from common.entities import Pipeline, Run, RunStatus, RunTask, Task


@pytest.fixture
def pipelines(client, company, organization, project):
    yield [
        Pipeline.create(key="PI1", project=project),
        Pipeline.create(key="PI2", project=project),
    ]


@pytest.fixture
def tasks(pipelines):
    tasks = {}
    for pipeline in pipelines:
        tasks[pipeline] = [
            Task.create(key=f"test task{pipeline.id}-{i}", name="TaskName", pipeline=pipeline) for i in range(6)
        ]
    yield tasks


@pytest.fixture
def runs(pipelines):
    runs = {}
    for pipeline in pipelines:
        runs[pipeline] = Run.create(
            key=f"Key Pipeline #{pipeline.id}", pipeline=pipeline, status=RunStatus.RUNNING.name
        )
    yield runs


@pytest.fixture
def run_tasks(runs, pipelines, tasks):
    base_start = datetime.now()

    run_tasks = {}
    for pipeline in pipelines:
        pipeline_run = runs[pipeline]
        run_tasks[pipeline_run] = [
            RunTask.create(run=pipeline_run, task=t, start_time=(base_start - timedelta(hours=n)))
            for n, t in enumerate(tasks[pipeline])
        ]
    yield run_tasks


@pytest.mark.integration
def test_list_runtasks_ok(client, g_user, run_tasks, runs, tasks, pipelines):
    run = runs[pipelines[0]]
    response = client.get(f"/observability/v1/runs/{run.id}/tasks")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["total"] == len(run_tasks[run])

    tasks_in_pipeline = tasks[pipelines[0]]
    for rt in data["entities"]:
        assert any(rt["id"] == str(t.id) for t in run_tasks[run])
        assert any(rt["task"]["id"] == str(t.id) for t in tasks_in_pipeline)
        assert any(rt["task"]["key"] == t.key for t in tasks_in_pipeline)
        assert any(rt["task"]["display_name"] == t.display_name for t in tasks_in_pipeline)
        assert len(rt["task"]) == 3

    sorted_results = sorted(data["entities"], key=lambda r: datetime.fromisoformat(r["start_time"]))
    # check ascending time sort
    assert sorted_results == data["entities"]


@pytest.mark.integration
def test_list_runtasks_not_found(client, g_user):
    response = client.get(f"/observability/v1/runs/{str(uuid4())}/tasks")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_admin_user_list_runtasks_not_found(client, g_user_2_admin):
    response = client.get(f"/observability/v1/runs/{str(uuid4())}/tasks")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_admin_user_list_runtasks_ok(client, g_user_2_admin, run_tasks, runs, tasks, pipelines):
    # Admin user is allowed to access resources from any company
    run = runs[pipelines[0]]
    run_company = run.pipeline.project.organization.company.id
    user_company = g_user_2_admin.user.primary_company.id
    assert run_company != user_company

    response = client.get(f"/observability/v1/runs/{run.id}/tasks")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["total"] == len(run_tasks[run])


@pytest.mark.integration
def test_non_admin_user_list_runtasks_forbidden(client, g_user, company_2, organization_2, project_2):
    # Non-admin users can only access resources from their primary company
    pipeline_2 = Pipeline.create(key="company_2 pipeline", project=project_2)
    run = Run.create(key=f"Run-{pipeline_2.id}", pipeline=pipeline_2, status=RunStatus.RUNNING.name)
    task = Task.create(key=f"Task-{pipeline_2.id}", pipeline=pipeline_2)
    _ = RunTask.create(run=run, task=task)

    run_company = run.pipeline.project.organization.company.id
    user_company = g_user.primary_company.id
    assert run_company != user_company

    response = client.get(f"/observability/v1/runs/{run.id}/tasks")

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_runtasks_no_auth_forbidden(client, run_tasks, runs, tasks, pipelines):
    run = runs[pipelines[0]]
    response = client.get(f"/observability/v1/runs/{run.id}/tasks")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
