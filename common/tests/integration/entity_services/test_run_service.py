from datetime import datetime, timedelta

import pytest

from common.entities import Company, Organization, Pipeline, Project, Run, RunStatus, RunTask, Task
from common.entity_services import RunService
from common.entity_services.helpers import ListRules, SortOrder


@pytest.fixture
def pipelines(test_db):
    company = Company.create(name="Foo")
    organization = Organization.create(name="O1", company=company)
    project = Project.create(name="PR1", organization=organization, active=True)
    yield [
        Pipeline.create(key="PI1", project=project),
        Pipeline.create(key="PI2", project=project),
    ]


@pytest.fixture
def tasks(pipelines):
    tasks = {}
    for pipeline in pipelines:
        tasks[pipeline] = [Task.create(key=f"test task{pipeline.id}-{i}", pipeline=pipeline) for i in range(6)]
    yield tasks


@pytest.fixture
def runs(pipelines):
    runs = {}
    for pipeline in pipelines:
        runs[pipeline] = Run.create(
            key=f"Tag Pipeline #{pipeline.id}", pipeline=pipeline, status=RunStatus.RUNNING.name
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
def test_list_runtasks_with_rules(pipelines, runs, run_tasks, tasks):
    rs = RunService.get_runtasks_with_rules(runs[pipelines[0]].id, ListRules())
    # this is a little complicated. But to test we selected what we did, we need multiple other ids with data
    assert len(rs.results) == len(run_tasks[runs[pipelines[0]]])

    for r in rs.results:
        assert r.run.id == runs[pipelines[0]].id

    sorted_results = sorted(rs.results, key=lambda r: r.start_time)
    # check ascending time sort
    assert sorted_results == rs.results

    rs = RunService.get_runtasks_with_rules(runs[pipelines[0]].id, ListRules(sort=SortOrder.DESC.value))
    sorted_results = sorted(rs.results, key=lambda r: r.start_time)[::-1]
    assert sorted_results == rs.results
