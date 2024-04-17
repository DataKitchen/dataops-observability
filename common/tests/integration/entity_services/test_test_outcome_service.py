import copy

import pytest

from common.entities import TestgenDatasetComponent, TestGenTestOutcomeIntegration, TestOutcome
from common.entity_services import TestOutcomeService


@pytest.mark.integration
def test_insert_test_outcomes(test_outcomes_event, test_db, pipeline, instance_instance_set):
    TestOutcomeService.insert_from_event(
        event=test_outcomes_event,
        run_id=test_outcomes_event.run_id,
        component_id=pipeline.id,
        instance_set_id=instance_instance_set.instance_set_id,
    )
    results = list(TestOutcome.select())
    assert len(results) == 5
    for i, result in enumerate(results):
        assert result.name == test_outcomes_event.test_outcomes[i].name
        assert result.status == test_outcomes_event.test_outcomes[i].status
        assert result.description == test_outcomes_event.test_outcomes[i].description
        assert result.start_time == test_outcomes_event.test_outcomes[i].start_time
        assert result.end_time == test_outcomes_event.test_outcomes[i].end_time
        assert result.metric_value == test_outcomes_event.test_outcomes[i].metric_value
        assert result.min_threshold == test_outcomes_event.test_outcomes[i].min_threshold
        assert result.max_threshold == test_outcomes_event.test_outcomes[i].max_threshold
        assert result.task_id == test_outcomes_event.task_id
        assert result.run_id == test_outcomes_event.run_id
        assert result.external_url == test_outcomes_event.external_url


@pytest.mark.integration
def test_insert_test_outcomes_empty_list(test_outcomes_event, test_db, pipeline):
    test_outcomes_event.test_outcomes = []
    TestOutcomeService.insert_from_event(
        event=test_outcomes_event,
        run_id=test_outcomes_event.run_id,
        component_id=pipeline.id,
    )
    assert 0 == TestOutcome.select().count()


@pytest.mark.integration
def test_insert_test_outcomes_default_time(test_outcomes_event, test_db, pipeline):
    test_outcomes_event_copy = copy.deepcopy(test_outcomes_event)
    test_outcome = test_outcomes_event_copy.test_outcomes[0]
    test_outcome.start_time, test_outcome.end_time = None, None
    test_outcomes_event_copy.test_outcomes = [test_outcome]

    TestOutcomeService.insert_from_event(
        event=test_outcomes_event_copy,
        run_id=test_outcomes_event.run_id,
        component_id=pipeline.id,
    )
    result = TestOutcome.get()
    assert result.name == test_outcomes_event.test_outcomes[0].name
    assert result.start_time is not None
    assert result.start_time == test_outcomes_event.event_timestamp
    assert result.end_time is not None
    assert result.end_time == result.start_time


@pytest.mark.integration
def test_insert_test_outcomes_with_testgen_component(test_outcomes_testgen_event, test_db, pipeline, run):
    assert 0 == TestgenDatasetComponent.select().count()
    assert 0 == TestGenTestOutcomeIntegration.select().count()
    assert 0 == TestOutcome.select().count()
    # raise Exception(test_outcomes_testgen_event.component_integrations.integrations.testgen)
    # raise Exception(test_outcomes_testgen_event.component_integrations.integrations.testgen)
    # raise Exception(test_outcomes_testgen_event.test_outcomes[0].integrations.testgen)
    TestOutcomeService.insert_from_event(event=test_outcomes_testgen_event, run_id=run.id, component_id=pipeline.id)

    test_outcomes = TestOutcome.select()
    assert 1 == test_outcomes.count()
    test_outcome = test_outcomes.get()

    testgen_integrations = TestGenTestOutcomeIntegration.select()
    assert 1 == testgen_integrations.count()
    testgen_integration = testgen_integrations.get()
    assert test_outcome == testgen_integration.test_outcome
    assert "table1" == testgen_integration.table

    testgen_components = TestgenDatasetComponent.select()
    assert 1 == testgen_components.count()
    testgen_component = testgen_components.get()
    assert pipeline.id == testgen_component.component.id
    assert "redshift_db" == testgen_component.database_name

    # Update existing TestgenDatasetComponent when integrations changed
    event2 = copy.deepcopy(test_outcomes_testgen_event)
    event2.component_integrations.integrations.testgen.database_name = "other"
    TestOutcomeService.insert_from_event(event=event2, run_id=run.id, component_id=pipeline.id)
    testgen_components = TestgenDatasetComponent.select()
    assert 1 == testgen_components.count()
    testgen_component = testgen_components.get()
    assert pipeline.id == testgen_component.component.id
    assert "other" == testgen_component.database_name
