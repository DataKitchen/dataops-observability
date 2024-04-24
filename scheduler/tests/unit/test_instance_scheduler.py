from unittest.mock import patch

import pytest

from common.kafka import TOPIC_SCHEDULED_EVENTS
from testlib.fixtures.entities import *


@pytest.mark.unit
def test_instance_scheduler_produce_event(instance_rule_start, instance_rule_source, event_producer_mock, run_time):
    instance_rule_source._produce_event(instance_rule=instance_rule_start, run_time=run_time)

    (topic, event), _ = event_producer_mock.produce.call_args_list[0]
    assert topic == TOPIC_SCHEDULED_EVENTS
    assert event.partition_identifier == str(instance_rule_start.journey.project.id)
    assert event.project_id == instance_rule_start.journey.project.id
    assert event.journey_id == instance_rule_start.journey.id
    assert event.instance_rule_id == instance_rule_start.id
    assert event.instance_rule_action == instance_rule_start.action
    assert event.timestamp == run_time


@pytest.mark.unit
def test_instance_scheduler_add_job(instance_rule_start, instance_rule_source, scheduler):
    with patch.object(instance_rule_source, "add_job") as add_job_mock:
        instance_rule_source._create_and_add_job(instance_rule=instance_rule_start)

    job_kwargs = add_job_mock.call_args_list[0][1]
    assert job_kwargs.keys() == {"job_id", "trigger", "kwargs"}
    assert job_kwargs["job_id"] == str(instance_rule_start.id) + ":" + instance_rule_start.action.value
    assert job_kwargs["kwargs"].keys() == {"instance_rule", "run_time"}
    assert job_kwargs["kwargs"]["instance_rule"] == instance_rule_start
