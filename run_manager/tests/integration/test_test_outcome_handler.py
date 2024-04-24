import copy
from datetime import datetime

import pytest

from common.entities import (
    AlertLevel,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceAlertType,
    InstanceSet,
    RunTask,
    Task,
    TestgenDatasetComponent,
    TestGenTestOutcomeIntegration,
    TestOutcome,
)
from common.events.base import InstanceRef
from common.events.v1.event import EVENT_ATTRIBUTES
from common.events.v1.test_outcomes_event import TestOutcomeItem, TestStatuses
from observability_api.tests.integration.v1_endpoints.conftest import TIMESTAMP_FORMAT
from run_manager.alerts import INSTANCE_ALERT_LEVELS
from run_manager.context import RunManagerContext
from run_manager.event_handlers import TestOutcomeHandler

NUM_TEST_ITEMS = 10


@pytest.fixture
def task(pipeline):
    return Task.create(key="task1", pipeline=pipeline)


@pytest.fixture
def run_task(run, task):
    return RunTask.create(run=run, task=task)


@pytest.mark.integration
def test_test_outcome_handler_insert_run_test_outcomes(test_outcomes_event, run, pipeline, instance_instance_set):
    event = copy.deepcopy(test_outcomes_event)
    event.pipeline_id = pipeline.id
    event.run_id = run.id
    event.task_key = None
    event.test_outcomes = [TestOutcomeItem(name=f"n{i}", status="FAILED") for i in range(NUM_TEST_ITEMS)]
    instance_ref = InstanceRef(
        journey=instance_instance_set.instance.journey_id, instance=instance_instance_set.instance_id
    )
    handler = TestOutcomeHandler(
        RunManagerContext(
            run=run, component=pipeline, instances=[instance_ref], instance_set=instance_instance_set.instance_set
        )
    )
    handler.handle_test_outcomes(event)

    assert Task.select().count() == 0
    assert RunTask.select().count() == 0
    assert TestOutcome.select().get().instance_set.iis.count() == 1
    tests = TestOutcome.select()
    assert tests.count() == NUM_TEST_ITEMS
    assert all(t.external_url == event.external_url for t in tests)
    assert len(handler.alerts) == 1
    alert = handler.alerts[0]
    assert alert.type == InstanceAlertType.TESTS_FAILED
    assert alert.level == AlertLevel.ERROR
    assert alert.description == f"Batch Pipeline ‘{pipeline.display_name}’ tests failed"

    assert InstanceAlert.select().count() == 1
    alert_model = InstanceAlert.select().get()
    assert [iac.component_id for iac in alert_model.iac] == [pipeline.id]


@pytest.mark.integration
def test_test_outcome_handler_insert_test_outcomes_testgen(
    test_outcomes_testgen_event, run, pipeline, test_outcome_item_data
):
    assert 0 == TestgenDatasetComponent.select().count()
    assert 0 == TestGenTestOutcomeIntegration.select().count()
    assert 0 == TestOutcome.select().count()

    handler = TestOutcomeHandler(RunManagerContext(run=run, component=pipeline, instances=[], instance_set=[]))
    handler.handle_test_outcomes(test_outcomes_testgen_event)
    test_outcomes = TestOutcome.select()
    assert 1 == test_outcomes.count()
    test_outcome = test_outcomes.get()
    expected_test_outcome_data = {
        key: value for key, value in test_outcome_item_data.items() if key not in ["metadata", "integrations"]
    }
    for key, value in expected_test_outcome_data.items():
        if key in ["start_time", "end_time"]:
            assert getattr(test_outcome, key) == datetime.strptime(value, TIMESTAMP_FORMAT)
        else:
            assert getattr(test_outcome, key) == value

    testgen_components = TestgenDatasetComponent.select()
    assert 1 == testgen_components.count()
    testgen_component = testgen_components.get()
    assert pipeline.id == testgen_component.component.id
    assert "redshift_db" == testgen_component.database_name

    testgen_integrations = TestGenTestOutcomeIntegration.select()
    assert 1 == testgen_integrations.count()
    testgen_integration = testgen_integrations.get()
    assert test_outcome == testgen_integration.test_outcome
    assert "table1" == testgen_integration.table


@pytest.mark.integration
def test_test_outcome_handler_insert_task_test_outcomes(test_outcomes_event, run, pipeline, task, run_task):
    event = copy.deepcopy(test_outcomes_event)
    event.pipeline_id = pipeline.id
    event.run_id = run.id
    event.task_key = "Test Outcome task"
    event.test_outcomes = [TestOutcomeItem(name=f"n{i}", status="FAILED") for i in range(NUM_TEST_ITEMS)]

    handler = TestOutcomeHandler(RunManagerContext(run=run, task=task, run_task=run_task, component=pipeline))
    handler.handle_test_outcomes(event)

    tests = TestOutcome.select()
    assert tests.count() == NUM_TEST_ITEMS
    assert all(t.external_url == event.external_url for t in tests)


@pytest.mark.integration
@pytest.mark.parametrize("event_key", ("dataset_key", "server_key", "stream_key"))
def test_test_outcome_handler_non_pipeline_components_insert(
    event_key, request, test_outcomes_event, instance_instance_set, run, project
):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(test_outcomes_event)
    event.pipeline_key = None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_id, component.id)
    event.test_outcomes = [TestOutcomeItem(name=f"n{i}", status="FAILED") for i in range(NUM_TEST_ITEMS)]

    instance_ref = InstanceRef(
        journey=instance_instance_set.instance.journey_id, instance=instance_instance_set.instance_id
    )
    handler = TestOutcomeHandler(
        RunManagerContext(
            run=None,
            component=component,
            instances=[instance_ref],
            instance_set=instance_instance_set.instance_set,
        )
    )
    handler.handle_test_outcomes(event)

    tests = TestOutcome.select()
    assert tests.count() == NUM_TEST_ITEMS
    assert all(t.external_url == event.external_url for t in tests)
    assert len(handler.alerts) == 1


@pytest.mark.integration
def test_test_outcome_handler_insert_batch_pipeline_test_outcomes_missing_run(test_outcomes_event, run, pipeline):
    event = copy.deepcopy(test_outcomes_event)
    event.pipeline_id = pipeline.id
    event.test_outcomes = [TestOutcomeItem(name=f"n{i}", status="FAILED") for i in range(NUM_TEST_ITEMS)]

    handler = TestOutcomeHandler(RunManagerContext(run=None, component=pipeline))
    handler.handle_test_outcomes(event)

    assert Task.select().count() == 0
    assert RunTask.select().count() == 0
    assert TestOutcome.select().count() == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "test_status,pre_existing_alert,expected_count",
    (
        (TestStatuses.FAILED, InstanceAlertType.TESTS_FAILED, 0),
        (TestStatuses.WARNING, InstanceAlertType.TESTS_HAD_WARNINGS, 0),
        (TestStatuses.PASSED, None, 0),
        (TestStatuses.FAILED, InstanceAlertType.TESTS_HAD_WARNINGS, 1),
        (TestStatuses.WARNING, InstanceAlertType.TESTS_FAILED, 1),
    ),
    ids=(
        "Same status, FAILED",
        "Same status, WARNING",
        "Tests passed",
        "Different status, FAILED",
        "Different status, WARNING",
    ),
)
def test_test_outcome_handler_create_alert_skip_existing(
    test_status, pre_existing_alert, expected_count, test_outcomes_event, pipeline, instance_instance_set
):
    event = copy.deepcopy(test_outcomes_event)
    event.pipeline_id = pipeline.id
    event.test_outcomes = [TestOutcomeItem(name="Test", status=test_status.name)]
    instance_ref = InstanceRef(
        journey=instance_instance_set.instance.journey_id, instance=instance_instance_set.instance_id
    )
    handler = TestOutcomeHandler(
        RunManagerContext(component=pipeline, instances=[instance_ref], instance_set=instance_instance_set.instance_set)
    )
    if pre_existing_alert:
        alert = InstanceAlert.create(
            instance=instance_instance_set.instance,
            type=pre_existing_alert,
            description="x",
            level=INSTANCE_ALERT_LEVELS[pre_existing_alert],
        )
        InstanceAlertsComponents.create(component=pipeline, instance_alert=alert)

    handler.create_instance_alerts(event)

    assert len(handler.alerts) == expected_count


@pytest.mark.integration
def test_test_outcome_handler_create_alert_multiple_instances(test_outcomes_event, dataset, journey):
    event = copy.deepcopy(test_outcomes_event)
    event.pipeline_key = None
    event.dataset_key = dataset.key
    event.dataset_id = dataset.id
    event.test_outcomes = [TestOutcomeItem(name="Test", status=TestStatuses.WARNING.name)]

    instances = [InstanceRef(journey=journey.id, instance=Instance.create(journey=journey).id) for _ in range(3)]
    instance_set = InstanceSet.get_or_create([ref.instance for ref in instances])
    handler = TestOutcomeHandler(RunManagerContext(component=dataset, instances=instances, instance_set=instance_set))

    handler.create_instance_alerts(event)

    assert len(handler.alerts) == 3


@pytest.mark.integration
def test_test_outcome_handler_create_alert_multiple_components(
    test_outcomes_event, journey, instance_instance_set, request
):
    for event_key in ("dataset_key", "server_key", "stream_key"):
        event = copy.deepcopy(test_outcomes_event)
        event.pipeline_key = None
        component = request.getfixturevalue(event_key[:-4])
        setattr(event, event_key, component.key)
        setattr(event, "component_id", component.id)

        event.test_outcomes = [TestOutcomeItem(name="Test", status=TestStatuses.WARNING.name)]

        instance_ref = InstanceRef(
            journey=instance_instance_set.instance.journey_id, instance=instance_instance_set.instance_id
        )
        handler = TestOutcomeHandler(
            RunManagerContext(
                component=component, instances=[instance_ref], instance_set=instance_instance_set.instance_set
            )
        )

        handler.create_instance_alerts(event)

        assert len(handler.alerts) == 1
