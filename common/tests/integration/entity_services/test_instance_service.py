from datetime import datetime, timedelta

import pytest

from common.entities import Instance, InstanceSet, Run, RunStatus, TestOutcome
from common.entity_services import InstanceService
from common.events.v1 import TestStatuses


@pytest.mark.integration
def test_aggregate_runs_summary(journey, pipeline, patched_instance_set):
    instance_1 = Instance.create(journey=journey)
    instance_2 = Instance.create(journey=journey)
    instance_set_1 = InstanceSet.get_or_create([instance_1.id])
    instance_set_2 = InstanceSet.get_or_create([instance_1.id, instance_2.id])

    for i in range(8):
        Run.create(
            instance_set=instance_set_1 if i < 4 else instance_set_2,
            key=f"R{i}",
            pipeline=pipeline,
            status=RunStatus.FAILED.name if i % 2 else RunStatus.COMPLETED.name,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(minutes=5),
        )
    InstanceService.aggregate_runs_summary([instance_1, instance_2])
    assert len(instance_1.runs_summary) == 2
    assert {"status": "FAILED", "count": 4} in instance_1.runs_summary
    assert {"status": "COMPLETED", "count": 4} in instance_1.runs_summary
    assert {"status": "FAILED", "count": 2} in instance_2.runs_summary
    assert {"status": "COMPLETED", "count": 2} in instance_2.runs_summary


@pytest.mark.integration
def test_aggregate_tests_summary(journey, pipeline, patched_instance_set):
    instance_1 = Instance.create(journey=journey)
    instance_2 = Instance.create(journey=journey)
    instance_set_1 = InstanceSet.get_or_create([instance_1.id])
    instance_set_2 = InstanceSet.get_or_create([instance_1.id, instance_2.id])

    for i in range(8):
        TestOutcome.create(
            instance_set=instance_set_1 if i < 4 else instance_set_2,
            component=pipeline,
            name="My test",
            status=TestStatuses.FAILED.name if i % 2 else TestStatuses.WARNING.name,
        )
    InstanceService.aggregate_tests_summary([instance_1, instance_2])
    assert len(instance_1.tests_summary) == 2
    assert {"status": "FAILED", "count": 4} in instance_1.tests_summary
    assert {"status": "WARNING", "count": 4} in instance_1.tests_summary
    assert {"status": "FAILED", "count": 2} in instance_2.tests_summary
    assert {"status": "WARNING", "count": 2} in instance_2.tests_summary
