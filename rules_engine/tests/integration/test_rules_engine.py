import copy
import logging
from unittest.mock import MagicMock, patch

import pytest

from common.entities import Rule as RuleEntity
from common.entities import RunStatus
from common.events.v1 import TestStatuses
from common.events.v1.test_outcomes_event import TestOutcomeItem
from common.predicate_engine.query import ANY, R
from rules_engine import lib
from rules_engine.engine import RulesEngine
from rules_engine.rules import Rule, get_rules

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.integration
def test_rules_engine_matching_task(kafka_consumer, db_rule, run_status_event, journey):
    kafka_consumer.__iter__.return_value = iter((run_status_event,))

    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value=None)

    # This rule spans to the actual task attribute
    # This should be an affirmative match
    predicate = R(event__task__key__exact="T1")
    # Register the rule manually
    Rule(predicate, db_rule, action, journey_id=journey.id).register()

    rules_engine.process_events()
    # If the action as triggered then the match was successful
    action.assert_called_with(run_status_event.payload, db_rule, journey.id)


@pytest.mark.integration
def test_rules_engine_non_matching_pipeline(kafka_consumer, db_rule, run_status_event, journey, journey_dag):
    kafka_consumer.__iter__.return_value = iter((run_status_event,))

    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value=None)
    # This should not match
    predicate = R(event__task__key__exact="T2")
    # Register the rule manually
    Rule(predicate, db_rule, action, journey_id=journey.id).register()

    rules_engine.process_events()
    # If the action as triggered then the match was successful - this shouldn't happen
    action.assert_not_called()


@pytest.mark.integration
def test_rules_engine_matching_status(kafka_consumer, db_rule, run_status_event, journey):
    kafka_consumer.__iter__.return_value = iter((run_status_event,))

    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value=None)

    # This rule spans to the actual task attribute
    # This should be an affirmative match
    predicate = R(event__status__exact=RunStatus.RUNNING.name)
    # Register the rule manually
    Rule(predicate, db_rule, action, journey_id=journey.id).register()

    rules_engine.process_events()
    # If the action as triggered then the match was successful
    action.assert_called_with(run_status_event.payload, db_rule, journey.id)


@pytest.mark.integration
@pytest.mark.parametrize(
    "event_fixture, component_fixture",
    [
        ("batch_pipeline_test_outcome_event_message", "pipeline"),
        ("dataset_test_outcome_event_message", "dataset"),
        ("server_test_outcome_event_message", "server"),
        ("streaming_pipeline_test_outcome_event_message", "stream"),
    ],
)
def test_rules_engine_matching_single_test_outcome(
    event_fixture, component_fixture, kafka_consumer, db_rule, journey, request
):
    event = request.getfixturevalue(event_fixture)
    component = request.getfixturevalue(component_fixture)
    assert len(event.payload.test_outcomes) == 1

    failed_test_outcome_event = copy.deepcopy(event)
    failed_test_outcome_event.payload.test_outcomes[0].status = TestStatuses.FAILED.name
    kafka_consumer.__iter__.return_value = iter((failed_test_outcome_event,))

    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value=None)

    predicate = R(event__test_outcomes__exact=ANY(TestStatuses.PASSED.name, attr_name="status"))
    Rule(predicate, db_rule, action, journey_id=journey.id, component_id=component.id).register()

    rules_engine.process_events()
    # No action triggers when there is not any matching rule
    action.assert_not_called()

    kafka_consumer.__iter__.return_value = iter((event,))
    rules_engine.process_events()
    action.assert_called_once_with(event.payload, db_rule, journey.id)


@pytest.mark.integration
@pytest.mark.parametrize(
    "event_fixture",
    [
        "batch_pipeline_test_outcome_event_message",
        "dataset_test_outcome_event_message",
        "server_test_outcome_event_message",
        "streaming_pipeline_test_outcome_event_message",
    ],
)
def test_rules_engine_multiple_test_outcomes_action_trigger_once(
    event_fixture, request, kafka_consumer, db_rule, journey
):
    test_outcome_event = request.getfixturevalue(event_fixture)
    for i in range(10):
        item = TestOutcomeItem(
            name=f"n{i}", status=f"{TestStatuses.PASSED.name if i % 2 == 0 else TestStatuses.FAILED.name}"
        )
        test_outcome_event.payload.test_outcomes.append(item)

    assert len(test_outcome_event.payload.test_outcomes) > 1
    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value=None)

    predicate = R(event__test_outcomes__exact=ANY(TestStatuses.PASSED.name, attr_name="status"))
    Rule(predicate, db_rule, action, journey_id=journey.id).register()

    kafka_consumer.__iter__.return_value = iter((test_outcome_event,))
    rules_engine.process_events()

    # An action should trigger once per one matching status
    action.assert_called_once_with(test_outcome_event.payload, db_rule, journey.id)


@pytest.mark.integration
def test_rules_engine_non_matching_status(kafka_consumer, run_status_event, db_rule, journey):
    kafka_consumer.__iter__.return_value = iter((run_status_event,))

    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value__exact=None)

    # This rule spans to the actual task attribute
    # This match should not succeed
    predicate = R(event__status__exact="nope")
    # Register the rule manually
    Rule(predicate, db_rule, action, journey_id=journey.id).register()

    rules_engine.process_events()
    # If the action as triggered then the match was successful
    action.assert_not_called()


@pytest.mark.integration
def test_register_rules_from_db(db_rule, fake_action_class, journey_dag):
    # Should only be 1 rule entry in the db right now
    assert 1 == RuleEntity.select().count()

    # Snag all the rules that aren't globally registered
    rules = [x for x in get_rules(journey_dag[0].journey)]
    assert 1 == len(rules)


@pytest.mark.integration
def test_rules_engine_matching_status_db(
    db_rule, kafka_consumer, run_status_event, fake_action_class, journey_dag, journey
):
    kafka_consumer.__iter__.return_value = iter((run_status_event,))
    rules_engine = RulesEngine(event_consumer=kafka_consumer)

    rules_engine.process_events()
    # If the action as triggered then the match was successful
    fake_action_class.return_value.execute.assert_called_with(run_status_event.payload, db_rule, journey.id)


@pytest.mark.integration
def test_rules_engine_process_multiple_component_types_simultaneously(
    db_rule, kafka_consumer, batch_pipeline_test_outcome_event_message, dataset_test_outcome_event_message, journey
):
    rules_engine = RulesEngine(event_consumer=kafka_consumer)
    action = MagicMock(return_value=None)

    predicate = R(event__test_outcomes__exact=ANY(TestStatuses.PASSED.name, attr_name="status"))
    Rule(predicate, db_rule, action, journey_id=journey.id).register()

    kafka_consumer.__iter__.return_value = iter(
        (batch_pipeline_test_outcome_event_message, dataset_test_outcome_event_message)
    )
    rules_engine.process_events()
    assert action.call_count == 2


@pytest.mark.integration
def test_rules_engine_consume_internal_instance_alert_event(kafka_consumer, internal_event_instance_alert_message):
    kafka_consumer.__iter__.return_value = iter((internal_event_instance_alert_message,))
    rules_engine = RulesEngine(event_consumer=kafka_consumer)

    with patch("rules_engine.engine.process_instance_alert") as process_mock:
        process_mock.return_value = None

        rules_engine.process_events()
        # If the action as triggered then the match was successful
        process_mock.assert_called_with(internal_event_instance_alert_message.payload)


@pytest.mark.integration
def test_rules_engine_consume_internal_run_alert_event(kafka_consumer, internal_event_run_alert_message):
    kafka_consumer.__iter__.return_value = iter((internal_event_run_alert_message,))
    rules_engine = RulesEngine(event_consumer=kafka_consumer)

    with patch("rules_engine.engine.process_run_alert") as process_mock:
        process_mock.return_value = None

        rules_engine.process_events()
        # If the action was triggered then the match was successful
        process_mock.assert_called_with(internal_event_run_alert_message.payload)


@pytest.mark.integration
def test_process_instance_alert(instance_alert_rule, fake_action_class, instance_alert, journey):
    lib.process_instance_alert(instance_alert)
    fake_action_class.return_value.execute.assert_called_with(instance_alert, instance_alert_rule, journey.id)


@pytest.mark.integration
def test_process_run_alert(run_state_rule, fake_action_class, run_alert, journey):
    lib.process_run_alert(run_alert)
    fake_action_class.return_value.execute.assert_called_with(run_alert, run_state_rule, journey.id)
