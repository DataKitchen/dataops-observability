from datetime import datetime, timedelta, timezone, UTC
from typing import Optional
from uuid import uuid4

import pytest

from common.actions.webhook_action import WebhookAction
from common.entities import (
    AlertLevel,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceAlertType,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Project,
    Run,
    RunAlert,
    RunAlertType,
    RunStatus,
    Server,
    TestOutcome,
    ActionImpl,
)
from common.entity_services import ProjectService
from common.entity_services.helpers import (
    ComponentFilters,
    Filters,
    ListRules,
    RunFilters,
    SortOrder,
    TestOutcomeItemFilters,
)
from common.events.v1 import TestStatuses
from common.exceptions.service import MultipleActionsFound
from testlib.fixtures.entities import *

NUMBER_OF_RUNS = 6


@pytest.fixture(autouse=True)
def local_test_db(test_db):
    yield test_db


def _add_runs(
    pipeline, instance, number_of_runs: int, current_time: datetime, *, expected_start_time: datetime | None = None
):
    instance_set = InstanceSet.get_or_create([instance.id])
    for key in range(1, number_of_runs + 1):
        r = Run.create(
            key=str(key),
            name=f"name{key}",
            pipeline=pipeline,
            instance_set=instance_set,
            start_time=(current_time - timedelta(hours=key)),
            end_time=(current_time + timedelta(hours=key)),
            expected_start_time=expected_start_time,
            status=RunStatus.COMPLETED.name if key % 2 == 0 else RunStatus.COMPLETED_WITH_WARNINGS.name,
        )
        RunAlert.create(
            name=f"alert {key}",
            description=f"Description of run alert {key}",
            level=AlertLevel["ERROR"].value,
            type=RunAlertType["LATE_END"].value,
            run=r,
        )

        common_args = dict(component=pipeline, run=r, instance_set=instance_set)
        TestOutcome.create(**common_args, name=f"TO-{r.id}-0", status=TestStatuses.PASSED.name)
        TestOutcome.create(**common_args, name=f"TO-{r.id}-1", status=TestStatuses.FAILED.name)
        TestOutcome.create(**common_args, name=f"TO-{r.id}-2", status=TestStatuses.FAILED.name)

    results = Run.select().where(Run.pipeline == pipeline)
    return results


@pytest.fixture
def runs(pipeline, current_time, instance, patched_instance_set):
    yield _add_runs(pipeline, instance, 6, current_time)


def _add_instances(journey, number_of_runs: int, current_time: datetime, project: Project):
    for offset in range(1, number_of_runs + 1):
        instance = Instance.create(
            journey=journey,
            start_time=(current_time - timedelta(hours=offset)),
            end_time=(current_time + timedelta(hours=offset)),
        )

        alert = InstanceAlert.create(
            name=f"alert {offset}",
            description=f"Description of instance {offset}",
            level=AlertLevel["ERROR"].value,
            type=InstanceAlertType["LATE_END"].value,
            instance=instance,
        )
        # need the UUID because of our unique constraint on pipeline keys.
        pipeline = Pipeline.create(key=f"P{offset}-{uuid4()}", project=project)
        _add_runs(pipeline=pipeline, instance=instance, number_of_runs=2, current_time=current_time)

        InstanceAlertsComponents.create(instance_alert=alert, component=pipeline)

    results = Instance.select().where(Instance.journey == journey)
    return results


@pytest.fixture
def instances(journey, project, current_time, patched_instance_set):
    yield _add_instances(journey=journey, project=project, current_time=current_time, number_of_runs=NUMBER_OF_RUNS)


@pytest.mark.integration
def test_get_runs_with_rules_asc(runs, pipeline):
    p = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], ListRules(), RunFilters())
    assert p.total == 6

    sorted_results = sorted(p.results, key=lambda x: x.start_time)
    assert sorted_results == p.results


@pytest.mark.integration
def test_get_run_with_rules_no_project_id(runs, pipeline):
    p = ProjectService.get_runs_with_rules(None, [str(pipeline.id)], ListRules(), RunFilters())
    assert p.total == 6

    sorted_results = sorted(p.results, key=lambda x: x.start_time)
    assert sorted_results == p.results


@pytest.mark.integration
def test_get_runs_with_rules_asc_no_ids(runs, pipeline):
    p = ProjectService.get_runs_with_rules(str(pipeline.project.id), [], ListRules(), RunFilters())
    assert p.total == 6

    sorted_results = sorted(p.results, key=lambda x: x.start_time)
    assert sorted_results == p.results


@pytest.mark.integration
def test_get_runs_with_rules_desc(runs, pipeline):
    p = ProjectService.get_runs_with_rules(
        str(pipeline.project.id), [str(pipeline.id)], ListRules(sort=SortOrder.DESC), RunFilters()
    )
    assert p.total == 6

    # Reverse the sort order and make sure it came back sorted descending
    sorted_results = sorted(p.results, key=lambda x: x.start_time)[::-1]
    assert sorted_results == p.results


@pytest.mark.integration
def test_get_runs_with_rules_coalesce_sort(pipeline, instance, patched_instance_set):
    instance_set = InstanceSet.get_or_create([instance.id])
    err_level = AlertLevel["ERROR"].value
    late_type = RunAlertType["LATE_END"].value

    r1_expected_start = datetime(2023, 5, 25, 7, 44, 1, tzinfo=UTC)
    r1 = Run.create(
        key="coalesce-run-1",
        pipeline=pipeline,
        instance_set=instance_set,
        expected_start_time=r1_expected_start,
        start_time=datetime(2023, 5, 25, 7, 44, 6, tzinfo=UTC),
        end_time=datetime(2023, 5, 25, 7, 45, 6, tzinfo=UTC),
        status=RunStatus.COMPLETED.name,
    )
    RunAlert.create(name="CA1", description="CD1", level=err_level, type=late_type, run=r1)

    r2_expected_start = datetime(2023, 5, 25, 7, 45, 10, tzinfo=UTC)
    r2 = Run.create(
        pipeline=pipeline,
        instance_set=instance_set,
        expected_start_time=r2_expected_start,
        start_time=None,
        end_time=None,
        status=RunStatus.PENDING.name,
    )
    RunAlert.create(name="CA2", description="CD2", level=err_level, type=late_type, run=r2)

    r3_expected_start = datetime(2023, 5, 25, 7, 46, 1, tzinfo=UTC)
    r3 = Run.create(
        key="coalesce-run-3",
        pipeline=pipeline,
        instance_set=instance_set,
        expected_start_time=r3_expected_start,
        start_time=datetime(2023, 5, 25, 7, 46, 22, tzinfo=UTC),
        end_time=datetime(2023, 5, 25, 7, 49, 12, tzinfo=UTC),
        status=RunStatus.COMPLETED_WITH_WARNINGS.name,
    )
    RunAlert.create(name="CA3", description="CD3", level=err_level, type=late_type, run=r3)

    # Ordering without the coalesce (by default nulls get sorted first). This is the old ordering prior to PD-1166;
    # this test is only to prove that the old ordering yields different results than sorting currently does (i.e. that
    # the test passing is not a fluke)
    expected_sort = [r2, r1, r3]
    actual_sort = list(Run.select().where(Run.pipeline == pipeline).order_by(Run.start_time))
    assert expected_sort == actual_sort

    # Test sorting in ascending order
    p_asc = ProjectService.get_runs_with_rules(
        str(pipeline.project.id), [str(pipeline.id)], ListRules(sort=SortOrder.ASC), RunFilters()
    )
    expected_asc = [r1, r2, r3]  # The expected sort order
    actual_asc = p_asc.results  # The actual sort order
    assert expected_asc == actual_asc

    # Test sorting in descending order
    p_desc = ProjectService.get_runs_with_rules(
        str(pipeline.project.id), [str(pipeline.id)], ListRules(sort=SortOrder.DESC), RunFilters()
    )
    expected_desc = [r3, r2, r1]  # The expected sort order
    actual_desc = p_desc.results  # The actual sort order
    assert expected_desc == actual_desc


@pytest.mark.integration
def test_get_runs_with_rules_paginated(runs, pipeline):
    rules = ListRules(sort=SortOrder.ASC, page=2, count=2)
    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, RunFilters())

    # Since we sort on start_time, we reverse the list given we've created the runs in reverse-time
    for key, r in enumerate(result.results[::-1], start=3):
        assert r.key == str(key)


@pytest.mark.integration
def test_get_runs_with_rules_time_filtering_start(runs, pipeline, current_time):
    rules = ListRules(sort=SortOrder.DESC)

    start_time = current_time - timedelta(hours=2)
    filters = RunFilters(start_range_begin=start_time, start_range_end=None)

    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)
    # Since we sort on start_time, we reverse the list given we've created the runs in reverse-time
    assert len(result.results) == 2
    for key, r in enumerate(result.results, start=1):
        assert r.start_time == (current_time - timedelta(hours=key))
        assert r.key == str(key)

    end_time = current_time - timedelta(hours=1)
    filters = RunFilters(start_range_begin=start_time, start_range_end=end_time)

    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)
    assert len(result.results) == 1
    assert result.results[0].start_time == (current_time - timedelta(hours=2))

    filters = RunFilters(pipeline_keys=["P1", "Unknown"])
    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)
    assert len(result.results) == 6
    filters = RunFilters(pipeline_keys=["Unknown"])
    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)
    assert len(result.results) == 0

    filters = RunFilters(run_keys=["1", "2"])
    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)
    assert sorted([r.key for r in result.results]) == sorted(["1", "2"])

    # ensure we see all these running together.
    end_time = current_time
    filters = RunFilters(
        start_range_begin=start_time, start_range_end=end_time, run_keys=["1", "2"], pipeline_keys=["P1", "Unknown"]
    )
    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)
    assert len(result.results) == 2


@pytest.mark.integration
def test_get_runs_with_rules_time_filtering_end(runs, pipeline, current_time):
    rules = ListRules(sort=SortOrder.DESC)

    end_time = current_time
    filters = RunFilters(end_range_begin=end_time, end_range_end=(end_time + timedelta(minutes=121)))
    result = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], rules, filters)

    assert len(result.results) == 2
    for idx, r in enumerate(result.results):
        expected = current_time + timedelta(hours=int(r.key))
        assert result.results[idx].end_time == expected


@pytest.mark.integration
def test_get_runs_with_rules_outcome_aggregation(runs, pipeline):
    p = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], ListRules(), RunFilters())
    assert p.total == 6

    expected_tests = (
        (TestStatuses.FAILED, 2),
        (TestStatuses.PASSED, 1),
    )
    for run in p.results:
        for (outcome, expected), actual in zip(
            sorted(expected_tests, key=lambda x: x[0].name), sorted(run.test_outcome_run, key=lambda x: x.status)
        ):
            assert (outcome.name, expected) == (actual.status, actual.count)


@pytest.mark.integration
def test_get_instances_with_rules_asc(instances, journey):
    p = ProjectService.get_instances_with_rules(
        ListRules(),
        Filters(),
        [str(journey.project.id)],
    )
    assert p.total == 6, [pr for pr in p]
    timestamps = [r.start_time for r in p.results]

    sorted_results = sorted(timestamps)
    assert sorted_results == timestamps


@pytest.mark.integration
def test_get_runs_with_status(runs, pipeline):
    p1 = ProjectService.get_runs_with_rules(str(pipeline.project.id), [str(pipeline.id)], ListRules(), RunFilters())
    assert p1.total == 6

    p2 = ProjectService.get_runs_with_rules(
        str(pipeline.project.id),
        [str(pipeline.id)],
        ListRules(),
        RunFilters(statuses=[RunStatus.COMPLETED_WITH_WARNINGS.name]),
    )
    assert p2.total == 3
    assert all(r.status == RunStatus.COMPLETED_WITH_WARNINGS.name for r in p2.results)


@pytest.mark.integration
def test_get_runs_with_rules_search(runs, pipeline):
    # Match key
    p1 = ProjectService.get_runs_with_rules(
        str(pipeline.project.id), [str(pipeline.id)], ListRules(search="4"), RunFilters()
    )
    assert p1.total == 1

    # Match name
    p2 = ProjectService.get_runs_with_rules(
        str(pipeline.project.id), [str(pipeline.id)], ListRules(search="name3"), RunFilters()
    )
    assert p2.total == 1

    # Partial case-insensitive match
    p3 = ProjectService.get_runs_with_rules(
        str(pipeline.project.id), [str(pipeline.id)], ListRules(search="ME6"), RunFilters()
    )
    assert p3.total == 1


@pytest.mark.integration
def test_get_instances_with_rules_has_alerts(instances, journey):
    p = ProjectService.get_instances_with_rules(
        ListRules(),
        Filters(),
        [str(journey.project.id)],
    )

    for entity in p.results:
        assert len(entity.alerts_summary) == 3, entity.alerts_summary
        instance_alerts = (
            InstanceAlert.select().where(InstanceAlert.instance == entity.id).order_by(InstanceAlert.created_on)
        )
        expected_desc = {i.description for i in instance_alerts}
        res_instance_alerts = [al for al in entity.alerts_summary if al["description"] in expected_desc]
        assert len(res_instance_alerts) == instance_alerts.count() and instance_alerts.count() == 1

        run_alerts = (
            RunAlert.select(RunAlert)
            .join(Run)
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .where(InstancesInstanceSets.instance == entity.id)
            .order_by(RunAlert.created_on)
        )
        expected_desc = {r.description for r in run_alerts}
        res_run_alerts = [al for al in entity.alerts_summary if al["description"] in expected_desc]
        assert len(res_run_alerts) == run_alerts.count() and run_alerts.count() == 2


@pytest.mark.integration
def test_get_instances_with_rules_asc_no_ids(instances, journey):
    p = ProjectService.get_instances_with_rules(
        ListRules(),
        Filters(),
        [str(journey.project.id)],
    )
    assert p.total == 6

    timestamps = [r.start_time for r in p.results]
    sorted_results = sorted(timestamps)
    assert sorted_results == timestamps


@pytest.mark.integration
def test_get_instances_with_rules_desc(instances, journey):
    p = ProjectService.get_instances_with_rules(
        ListRules(sort=SortOrder.DESC),
        Filters(),
        [str(journey.project.id)],
    )
    assert p.total == 6

    # Reverse the sort order and make sure it came back sorted descending
    timestamps = [r.start_time for r in p.results]
    sorted_results = sorted(timestamps)[::-1]
    assert sorted_results == timestamps


@pytest.mark.integration
def test_get_instances_with_rules_paginated(instances, journey, current_time):
    rules = ListRules(sort=SortOrder.ASC, page=2, count=2)
    result = ProjectService.get_instances_with_rules(
        rules,
        Filters(),
        [str(journey.project.id)],
    )

    assert len(result.results) == 2
    instance1, instance2 = result.results
    assert instance1.start_time == current_time - timedelta(hours=4)
    assert instance2.start_time == current_time - timedelta(hours=3)


@pytest.mark.integration
def test_get_instances_with_rules_time_filtering_start(instances, journey, current_time):
    rules = ListRules(sort=SortOrder.DESC)

    start_time = current_time - timedelta(hours=2)
    filters = Filters(start_range_begin=start_time, start_range_end=None)

    result = ProjectService.get_instances_with_rules(rules, filters, [str(journey.project.id)])
    # Since we sort on start_time, we reverse the list given we've created the instances in reverse-time
    assert len(result.results) == 2
    instance1, instance2 = result.results
    assert instance1.start_time == current_time - timedelta(hours=1)
    assert instance2.start_time == current_time - timedelta(hours=2)

    end_time = current_time - timedelta(hours=1)
    filters = Filters(start_range_begin=start_time, start_range_end=end_time)

    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )
    assert len(result.results) == 1
    assert result.results[0].start_time == (current_time - timedelta(hours=2))

    filters = Filters(journey_names=["J1", "Unknown"])
    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )
    assert len(result.results) == 6
    filters = Filters(journey_names=["Unknown"])
    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )
    assert len(result.results) == 0

    # ensure we see all these running together.
    end_time = current_time
    filters = Filters(start_range_begin=start_time, start_range_end=end_time, journey_names=["J1", "Unknown"])
    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )
    assert len(result.results) == 2


@pytest.mark.integration
def test_get_instances_with_rules_expected_end_time(instance, instance_rule_end, journey):
    p = ProjectService.get_instances_with_rules(
        ListRules(),
        Filters(),
        [str(journey.project.id)],
    )
    assert p.total == 1
    assert p.results[0].end_time is None
    assert p.results[0].expected_end_time is not None


@pytest.mark.integration
def test_get_instances_with_rules_time_filtering_sort_active(instances, journey, current_time):
    rules = ListRules(sort=SortOrder.DESC)
    filters = Filters(active=False)
    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )
    assert len(result.results) == 6

    filters = Filters(active=True)
    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )
    assert len(result.results) == 0


@pytest.mark.integration
def test_get_instances_with_rules_time_filtering_end(instances, journey, current_time):
    rules = ListRules(sort=SortOrder.DESC)

    end_time = current_time
    filters = Filters(end_range_begin=end_time, end_range_end=(end_time + timedelta(minutes=121)))
    result = ProjectService.get_instances_with_rules(
        rules,
        filters,
        [str(journey.project.id)],
    )

    assert len(result.results) == 2
    instance1, instance2 = result.results
    assert instance1.end_time == current_time + timedelta(hours=1)
    assert instance2.end_time == current_time + timedelta(hours=2)


@pytest.mark.integration
def test_get_journeys_with_rules_journey_exists(test_db, project, journey):
    rules_page = ProjectService.get_journeys_with_rules(project.id, ListRules())
    assert rules_page.total == 1
    assert len(rules_page.results) == 1
    assert rules_page.results[0].id == journey.id


@pytest.mark.integration
def test_get_journeys_with_rules_no_journey(test_db):
    journey_page = ProjectService.get_journeys_with_rules(str(uuid4()), ListRules())
    assert journey_page.total == 0
    assert len(journey_page.results) == 0


@pytest.mark.integration
def test_get_journeys_with_rules_search(test_db, project):
    for i in range(3):
        Journey.create(name=f"P{i}", project=project)

    # Uppercase Search
    journey_page = ProjectService.get_journeys_with_rules(project.id, ListRules(search="P"))
    assert journey_page.total == 3

    # Lowercase Search
    i_journey_page = ProjectService.get_journeys_with_rules(project.id, ListRules(search="p"))
    assert i_journey_page.total == 3


@pytest.mark.integration
def test_get_journeys_with_rules_component_filter(
    test_db, journey, pipeline, pipeline_2, pipeline_3, journey_dag_edges, project
):
    # Create some extra journeys that we know we should not see
    j1 = Journey.create(name="Journey-1", project=project)
    j2 = Journey.create(name="Journey-2", project=project)

    # Create a few unrelated JourneyDagEdges
    JourneyDagEdge.create(journey=journey, left=pipeline_2, right=pipeline_3)
    JourneyDagEdge.create(journey=j1, left=pipeline_2, right=pipeline_3)
    JourneyDagEdge.create(journey=j2, left=pipeline_2, right=pipeline_3)

    # Create an addtional journey that we *should* see returned
    j3 = Journey.create(name="Journey-3", project=project)
    JourneyDagEdge.create(journey=j3, left=pipeline, right=pipeline)

    journey_page = ProjectService.get_journeys_with_rules(
        project.id, ListRules(sort=SortOrder.ASC), component_id=str(pipeline.id)
    )
    results = journey_page.results
    journey_names = {x.name for x in results}
    assert journey.name in journey_names
    assert "Journey-3" in journey_names
    assert journey_page.total == 2


@pytest.mark.integration
def test_get_journeys_with_rules_search_no_results(test_db, project):
    for i in range(3):
        Journey.create(name=f"P{i}", project=project)
    journey_page = ProjectService.get_journeys_with_rules(project.id, ListRules(search="Q"))
    assert journey_page.total == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "keys, names, expected_result",
    [
        (["foo", "bar"], ["foo", "bar"], ["bar", "foo"]),
        (["p1", "p2"], ["foo", "bar"], ["bar", "foo"]),
        (["foo", "bar"], [None, None], ["bar", "foo"]),
        (["foo", "bar"], ["", ""], ["bar", "foo"]),
        (["foo", "bar"], ["", "bar"], ["bar", "foo"]),
    ],
    ids=["basic_case", "name_then_key", "null_name", "empty_string_name", "empty_string_name_doesnt_come_first"],
)
def test_get_components_with_rules_sorting(keys, names, expected_result, project):
    pipelines = []
    for key, name in zip(keys, names):
        pipelines.append(Pipeline.create(key=key, name=name, project=project))
    result = ProjectService.get_components_with_rules(project.id, ListRules(), ComponentFilters())
    assert [p.display_name for p in result] == expected_result


@pytest.mark.integration
def test_get_components_multiple_types(pipeline, project):
    server = Server.create(key=pipeline.key, project=project)
    result = ProjectService.get_components_with_rules(project.id, ListRules(search=pipeline.key), ComponentFilters())
    # compare a set instead of list because we're not testing order here
    assert {p.display_name for p in result} == {server.display_name, pipeline.display_name}


@pytest.mark.integration
@pytest.mark.parametrize(
    "num_instances", [0, 1, 3], ids=["run has 0 instances", "run with 1 instance", "run with multiple instances"]
)
def test_get_runs_with_rules_different_number_of_instances(num_instances, company, organization, patched_instance_set):
    project = Project.create(name="other project", organization=organization, active=True)
    journey = Journey.create(name="other journey", project=project)
    pipeline = Pipeline.create(key="other pipeline", project=project)
    Run.create(key="dummy run (with no instances)", pipeline=pipeline, status="RUNNING")

    instances = [Instance.create(journey=journey) for _ in range(num_instances)]
    instance_set = InstanceSet.get_or_create([inst.id for inst in instances]) if instances else None
    Run.create(key="other run", pipeline=pipeline, instance_set=instance_set, status="RUNNING")

    # Pre-check
    p1 = ProjectService.get_runs_with_rules(str(project.id), [str(pipeline.id)], ListRules(), RunFilters())
    assert p1.total == 2

    p2 = ProjectService.get_runs_with_rules(
        str(pipeline.project.id),
        [str(pipeline.id)],
        ListRules(),
        RunFilters(instance_ids=instances),
    )
    # If the instances filter is an empty list, it has no affect; hence, return all runs in the specified pipeline
    assert p2.total == 2 if num_instances == 0 else 1


@pytest.mark.integration
def test_get_test_outcomes_with_rules_no_project(test_db, project):
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), TestOutcomeItemFilters())
    assert test_outcomes_page.total == 0
    assert len(test_outcomes_page.results) == 0


@pytest.mark.integration
def test_get_test_outcome_project_no_runs_associated(test_db, project, run):
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), TestOutcomeItemFilters())
    assert test_outcomes_page.total == 0
    assert len(test_outcomes_page.results) == 0


@pytest.mark.integration
def test_get_test_outcome_project(test_db, project, run, test_outcomes_instance):
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), TestOutcomeItemFilters())
    assert test_outcomes_page.total == 5
    assert len(test_outcomes_page.results) == 5
    for test_outcome in test_outcomes_page:
        assert test_outcome.run_id == run.id


@pytest.mark.integration
def test_get_test_outcome_project_instance_filter(test_db, project, run, instance, test_outcomes_instance):
    filters = TestOutcomeItemFilters(instance_ids=[instance.id])
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), filters)
    assert test_outcomes_page.total == 5
    assert len(test_outcomes_page.results) == 5
    for test_outcome in test_outcomes_page:
        assert test_outcome.run_id == run.id


@pytest.mark.integration
def test_get_test_outcome_project_instance_filter_no_results(test_db, project, run, test_outcomes_instance):
    # Ensure there are TestOutcome instances that will be filtered out by the instance_id filter
    assert TestOutcome.select().exists(), "Expected database to contain TestOutcome instances"
    filters = TestOutcomeItemFilters(instance_ids=[str(uuid4())])
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), filters)
    assert test_outcomes_page.total == 0
    assert len(test_outcomes_page.results) == 0


@pytest.mark.integration
def test_get_test_outcome_project_run_filter(test_db, project, run, instance, test_outcomes_instance):
    filters = TestOutcomeItemFilters(run_ids=[run.id])
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), filters)
    assert test_outcomes_page.total == 5
    assert len(test_outcomes_page.results) == 5
    for test_outcome in test_outcomes_page:
        assert test_outcome.run_id == run.id


@pytest.mark.integration
def test_get_test_outcome_project_run_filter_no_results(test_db, project, run, instance, test_outcomes_instance):
    # Ensure there are TestOutcome instances that will be filtered out by the run_id filter
    assert TestOutcome.select().exists(), "Expected database to contain TestOutcome instances"
    filters = TestOutcomeItemFilters(run_ids=[str(uuid4())])
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), filters)
    assert test_outcomes_page.total == 0
    assert len(test_outcomes_page.results) == 0


@pytest.mark.integration
def test_get_test_outcome_project_search_key(test_db, project, run, test_outcomes_instance):
    search_string = test_outcomes_instance[0].name
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(
        project, ListRules(search=search_string), TestOutcomeItemFilters()
    )
    assert test_outcomes_page.total == 1
    assert len(test_outcomes_page.results) == 1
    for test_outcome in test_outcomes_page:
        assert test_outcome.run_id == run.id

    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(
        project, ListRules(search="QWERTY"), TestOutcomeItemFilters()
    )
    assert test_outcomes_page.total == 0
    assert len(test_outcomes_page.results) == 0


@pytest.mark.integration
def test_get_test_outcome_project_with_test_outcomes(test_db, project, run, test_outcomes_instance):
    test_outcomes_page = ProjectService.get_test_outcomes_with_rules(project, ListRules(), TestOutcomeItemFilters())
    assert test_outcomes_page.total == 5
    assert len(test_outcomes_page.results) == 5

    actual_outcomes = {
        TestStatuses.FAILED.name: 0,
        TestStatuses.PASSED.name: 0,
        TestStatuses.WARNING.name: 0,
    }

    for test_outcome in test_outcomes_page:
        assert test_outcome.run_id == run.id
        assert type(test_outcome) == TestOutcome
        actual_outcomes[test_outcome.status] += 1

    expected_outcomes = {
        TestStatuses.FAILED.name: 0,
        TestStatuses.PASSED.name: 3,
        TestStatuses.WARNING.name: 2,
    }

    assert expected_outcomes == actual_outcomes


@pytest.mark.integration
def test_get_template_actions(test_db, project, action):
    actions = ProjectService.get_template_actions(project, [ActionImpl.SEND_EMAIL, ActionImpl.CALL_WEBHOOK])

    assert len(actions) == 1
    assert actions[ActionImpl.SEND_EMAIL.name] == action


@pytest.mark.integration
def test_get_template_actions_multiple(test_db, project, action):
    action.id = uuid4()
    action.name += " 2"
    action.save(force_insert=True)

    with pytest.raises(MultipleActionsFound):
        actions = ProjectService.get_template_actions(project, [ActionImpl.SEND_EMAIL])


@pytest.mark.integration
def test_get_alert_actions(test_db, project):
    (webhook_action,) = ProjectService.get_alert_actions(project)

    assert isinstance(webhook_action, WebhookAction)
    assert webhook_action.override_arguments == project.alert_actions[0]["action_args"]


def test_get_alert_actions_empty(test_db, project):
    project.alert_actions = []

    actions = ProjectService.get_alert_actions(project)

    assert actions == []
