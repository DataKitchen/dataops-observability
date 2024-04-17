import copy
from datetime import datetime

import pytest

from common.entities import (
    Instance,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Run,
    RunStatus,
)
from common.events.v1.event import EVENT_ATTRIBUTES
from run_manager.context import RunManagerContext
from run_manager.event_handlers import InstanceHandler
from testlib.fixtures.v1_events import base_events, valid_event_keys


@pytest.fixture(autouse=True)
def patch_instance_set(patched_instance_set):
    yield patched_instance_set


@pytest.mark.integration
def test_run_status_event_identify_instances_no_journey(pipeline, journey, RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = pipeline.id
    handler = InstanceHandler(RunManagerContext(created_run=False))
    RUNNING_run_status_event.accept(handler)
    assert len(handler.context.instances) == 0
    assert handler.context.instance_set is None


@pytest.mark.integration
@pytest.mark.parametrize("event_key", [key for key in valid_event_keys if key != "pipeline_key"])
@pytest.mark.parametrize("base_event", base_events)
def test_other_events_identify_instances_no_journey(event_key, base_event, project, journey, request):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_id, component.id)
    handler = InstanceHandler(RunManagerContext(created_run=False))
    event.accept(handler)
    assert len(handler.context.instances) == 0
    assert handler.context.instance_set is None


@pytest.mark.integration
def test_run_status_event_identify_instances_create_new(journey, pipeline, run, RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = pipeline.id
    RUNNING_run_status_event.run_id = run.id
    JourneyDagEdge.create(journey=journey, right=pipeline)
    Instance.create(journey=journey, end_time=datetime.utcnow())

    assert Instance.select().count() == 1
    assert InstancesInstanceSets.select().count() == 0

    handler = InstanceHandler(RunManagerContext(started_run=True))
    RUNNING_run_status_event.accept(handler)
    instances = handler.context.instances

    assert Instance.select().count() == 2
    assert len(instances) == 1
    assert handler.context.instance_set.iis.count() == 1
    assert journey.id == instances[0].journey
    new_instance = Instance.get_by_id(instances[0].instance)
    assert new_instance.active
    assert new_instance.journey == journey


@pytest.mark.integration
@pytest.mark.parametrize("event_key", [key for key in valid_event_keys if key != "pipeline_key"])
@pytest.mark.parametrize("base_event", base_events)
def test_other_events_identify_instances_create_new(event_key, base_event, journey, dataset, request):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key = None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_id, component.id)
    JourneyDagEdge.create(journey=journey, right=component)
    Instance.create(journey=journey, end_time=datetime.utcnow())

    assert Instance.select().count() == 1
    assert InstancesInstanceSets.select().count() == 0

    handler = InstanceHandler(RunManagerContext(started_run=True))
    event.accept(handler)
    instances = handler.context.instances

    assert Instance.select().count() == 2
    assert len(instances) == 1
    assert journey.id == instances[0].journey
    new_instance = Instance.get_by_id(instances[0].instance)
    assert new_instance.active
    assert new_instance.journey == journey
    assert handler.context.instance_set.iis.count() == 1


@pytest.mark.integration
def test_run_status_event_identify_instances_reuse_active(journey, pipeline, RUNNING_run_status_event):
    Instance.create(journey=journey, end_time=datetime.utcnow())
    instance = Instance.create(journey=journey)
    instance_set = InstanceSet.get_or_create([instance.id])
    run = Run.create(key="testkey", pipeline=pipeline, status=RunStatus.RUNNING.name, instance_set=instance_set)
    RUNNING_run_status_event.pipeline_id = pipeline.id
    RUNNING_run_status_event.run_id = run.id
    JourneyDagEdge.create(journey=journey, right=pipeline)

    assert Instance.select().count() == 2
    handler = InstanceHandler(RunManagerContext(created_run=False))
    RUNNING_run_status_event.accept(handler)
    instances = handler.context.instances

    assert Instance.select().count() == 2
    assert len(instances) == 1
    assert handler.context.instance_set.iis.count() == 1
    assert instance.id == instances[0].instance
    assert journey.id == instances[0].journey

    assert (
        Run.select()
        .join(InstanceSet)
        .join(InstancesInstanceSets)
        .where(Run.id == run.id, InstancesInstanceSets.instance == instance.id)
        .count()
    ) == 1


@pytest.mark.integration
@pytest.mark.parametrize("event_key", [key for key in valid_event_keys if key != "pipeline_key"])
@pytest.mark.parametrize("base_event", base_events)
def test_other_events_identify_instances_reuse_active(event_key, base_event, journey, request):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    event.pipeline_key = None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_id, component.id)
    JourneyDagEdge.create(journey=journey, right=component)
    Instance.create(journey=journey, end_time=datetime.utcnow())
    instance = Instance.create(journey=journey)

    assert Instance.select().count() == 2
    handler = InstanceHandler(RunManagerContext(created_run=False))
    event.accept(handler)
    instances = handler.context.instances

    assert Instance.select().count() == 2
    assert len(instances) == 1
    assert handler.context.instance_set.iis.count() == 1
    assert instance.id == instances[0].instance
    assert journey.id == instances[0].journey


@pytest.mark.integration
def test_identify_instances_multiple_active_instances(journey, pipeline, run, RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = pipeline.id
    RUNNING_run_status_event.run_id = run.id
    JourneyDagEdge.create(journey=journey, right=pipeline)
    i1 = Instance.create(journey=journey)
    i2 = Instance.create(journey=journey)

    handler = InstanceHandler(RunManagerContext(created_run=False))
    RUNNING_run_status_event.accept(handler)
    instances = handler.context.instances
    assert len(instances) == 1
    assert handler.context.instance_set.iis.count() == 1
    assert instances[0].instance in (i1.id, i2.id)


@pytest.mark.integration
@pytest.mark.parametrize("event_key", valid_event_keys)
@pytest.mark.parametrize("base_event", base_events)
def test_identify_instances_multiple_journeys(event_key, base_event, project, request, run):
    component = request.getfixturevalue(event_key[:-4])
    event = copy.deepcopy(request.getfixturevalue(base_event))
    if event_key != "pipeline_key":
        event.pipeline_key = None
    setattr(event, event_key, component.key)
    setattr(event, EVENT_ATTRIBUTES.get(event_key).component_id, component.id)

    def journey_conf():
        yield from ((i, i % 2 == 0) for i in range(5))

    instance_ids = set()
    for i, create_instance in journey_conf():
        journey = Journey.create(name=f"Journey{i}", project=project)
        JourneyDagEdge.create(journey=journey, right=component)
        if create_instance:
            instance = Instance.create(journey=journey)
            instance_ids.add(instance.id)
            if event_key == "pipeline_key":
                event.run_id = run.id
    run.instance_set = InstanceSet.get_or_create(instance_ids)
    run.save()

    assert Instance.select().count() == sum(j for _, j in journey_conf())
    handler = InstanceHandler(RunManagerContext(started_run=True))
    event.accept(handler)
    instances = handler.context.instances
    expected_length = sum(1 for _ in journey_conf())
    assert Instance.select().count() == expected_length
    assert len(instances) == expected_length
    assert handler.context.instance_set.iis.count() == expected_length


@pytest.mark.integration
def test_identify_instances_one_instance_two_runs(project, journey, RUNNING_run_status_event):
    assert InstancesInstanceSets.select().count() == 0
    for i in range(2):
        pipeline = Pipeline.create(key=f"pipeline{i}", project=project)
        JourneyDagEdge.create(journey=journey, right=pipeline)
        run = Run.create(key=f"runkey{i}", pipeline=pipeline, status=RunStatus.RUNNING.name)
        RUNNING_run_status_event.pipeline_id = pipeline.id
        RUNNING_run_status_event.run_id = run.id
        handler = InstanceHandler(RunManagerContext(started_run=True))
        RUNNING_run_status_event.accept(handler)
        instances = handler.context.instances
        assert len(instances) == 1
        assert handler.context.instance_set.iis.count() == 1
        assert instances[0].instance == Instance.get().id
    assert Instance.select().count() == 1
    assert InstancesInstanceSets.select().count() == 1


@pytest.mark.integration
def test_identify_instances_event_for_closed_instance(project, journey, pipeline, run, RUNNING_run_status_event):
    RUNNING_run_status_event.pipeline_id = pipeline.id
    RUNNING_run_status_event.run_id = run.id
    JourneyDagEdge.create(journey=journey, right=pipeline)
    instance = Instance.create(journey=journey, end_time=datetime.utcnow())
    instance_set = InstanceSet.get_or_create([instance.id])
    run.instance_set = instance_set
    run.save()
    Instance.create(journey=journey)
    assert Instance.select().count() == 2
    handler = InstanceHandler(RunManagerContext(created_run=False))
    RUNNING_run_status_event.accept(handler)
    instances = handler.context.instances
    assert Instance.select().count() == 2
    assert len(instances) == 1
    assert handler.context.instance_set.iis.count() == 1
    assert instances[0].instance == instance.id
    assert InstanceSet.select().count() == 1
    assert InstancesInstanceSets.select().count() == 1
