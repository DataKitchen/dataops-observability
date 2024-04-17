from datetime import datetime

import pytest

from common.entities import (
    AlertLevel,
    Dataset,
    Instance,
    InstanceAlert,
    InstanceAlertType,
    InstanceSet,
    JourneyDagEdge,
    Pipeline,
    Run,
    RunStatus,
)
from common.entities.instance import InstanceStatus
from run_manager.context import RunManagerContext
from run_manager.event_handlers import IncompleteInstanceHandler


@pytest.mark.integration
def test_check_instance_with_finished_run(project, journey, instance):
    pipeline = Pipeline.create(project=project, key="p")
    dataset = Dataset.create(project=project, key="d")
    JourneyDagEdge.create(journey=journey, right=pipeline)
    JourneyDagEdge.create(journey=journey, right=dataset)
    iset = InstanceSet.get_or_create([instance.id])
    Run.create(pipeline=pipeline, key="r", instance_set=iset, status=RunStatus.FAILED.name)

    handler = IncompleteInstanceHandler(RunManagerContext(ended_instances=[instance.id]))
    handler.check()
    assert len(handler.alerts) == 0
    assert InstanceAlert.select().count() == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "run_status, run_start_time, run_key",
    (
        (RunStatus.RUNNING.name, datetime.now(), "key"),
        (RunStatus.MISSING.name, None, None),
        (RunStatus.PENDING.name, None, None),
    ),
)
def test_check_instance_with_incomplete_run(project, journey, instance, run_status, run_start_time, run_key):
    pipeline = Pipeline.create(project=project, key="p")
    dataset = Dataset.create(project=project, key="d")
    JourneyDagEdge.create(journey=journey, right=pipeline)
    JourneyDagEdge.create(journey=journey, right=dataset)
    iset = InstanceSet.get_or_create([instance.id])
    Run.create(pipeline=pipeline, key=run_key, instance_set=iset, status=run_status, start_time=run_start_time)

    handler = IncompleteInstanceHandler(RunManagerContext(ended_instances=[instance.id]))
    handler.check()
    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.type == InstanceAlertType.INCOMPLETE
    assert alert.level == AlertLevel.ERROR
    assert alert.instance == instance

    assert len(handler.alerts) == 1
    alert_event = handler.alerts[0]
    assert alert_event.type == alert.type
    assert alert_event.level == alert.level
    assert alert_event.instance_id == alert.instance_id
    assert alert_event.alert_id == alert.id

    assert Instance.select().count() == 1
    instance = Instance.get()
    assert instance.has_warnings is False
    assert instance.has_errors is True
    assert instance.status == InstanceStatus.ERROR.value


@pytest.mark.integration
def test_check_instance_with_nonexistent_run(project, journey, instance):
    pipeline = Pipeline.create(project=project, key="p")
    dataset = Dataset.create(project=project, key="d")
    JourneyDagEdge.create(journey=journey, right=pipeline)
    JourneyDagEdge.create(journey=journey, right=dataset)
    InstanceSet.get_or_create([instance.id])

    handler = IncompleteInstanceHandler(RunManagerContext(ended_instances=[instance.id]))
    handler.check()
    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.type == InstanceAlertType.INCOMPLETE
    assert alert.level == AlertLevel.ERROR
    assert alert.instance == instance

    assert len(handler.alerts) == 1
    alert_event = handler.alerts[0]
    assert alert_event.type == alert.type
    assert alert_event.level == alert.level
    assert alert_event.instance_id == alert.instance_id
    assert alert_event.alert_id == alert.id
