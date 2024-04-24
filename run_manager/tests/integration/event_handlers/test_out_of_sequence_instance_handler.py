from datetime import datetime, timezone

import pytest

from common.entities import (
    AlertLevel,
    Dataset,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceAlertType,
    InstanceSet,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Run,
    RunStatus,
)
from common.entities.instance import InstanceStatus
from common.events.base import InstanceRef
from run_manager.context import RunManagerContext
from run_manager.event_handlers.out_of_sequence_instance_handler import OutOfSequenceInstanceHandler


class JourneyContext:
    journey: Journey
    instance: Instance
    instance_set: InstanceSet
    dataset: Dataset
    pipelines: list[Pipeline]
    runs: list[Run]

    def __init__(self, project, pipelines=None, name="out-of-sequence-test"):
        self.journey = Journey.create(name=name, project=project)
        self.instance = Instance.create(journey=self.journey)
        self.instance_set = InstanceSet.get_or_create([self.instance.id])
        self.dataset = Dataset.create(key=f"{self.journey.name}-Dataset", project=self.journey.project)
        self.pipelines = pipelines or [
            Pipeline.create(key=f"{self.journey.name}-Pipeline{i}", project=self.journey.project) for i in range(5)
        ]
        self.runs = []
        for i in range(len(self.pipelines)):
            self.runs.append(
                Run.create(
                    key=f"{self.journey.name}-Run{i}",
                    pipeline=self.pipelines[i],
                    project=project,
                    instance_set=self.instance_set.id,
                    status=RunStatus.COMPLETED.name,
                    start_time=datetime.now(tz=timezone.utc),
                    end_time=datetime.now(tz=timezone.utc),
                )
            )
            JourneyDagEdge.create(
                journey=self.journey, left=self.pipelines[i - 1] if i > 0 else None, right=self.pipelines[i]
            )


@pytest.fixture
def journey_context(project):
    return JourneyContext(project=project)


@pytest.fixture
def journey_context2(project, journey_context):
    return JourneyContext(project, name="journey2", pipelines=journey_context.pipelines)


@pytest.fixture
def instance_ref(journey_context):
    return InstanceRef(journey_context.journey.id, journey_context.instance.id)


@pytest.fixture
def instance_ref2(journey_context2):
    return InstanceRef(journey_context2.journey.id, journey_context2.instance.id)


@pytest.fixture
def run_manager_context(instance_ref, journey_context):
    return RunManagerContext(
        started_run=True, run=journey_context.runs[2], component=journey_context.pipelines[2], instances=[instance_ref]
    )


@pytest.mark.integration
def test_in_sequence_runs_no_alert(journey_context, run_manager_context, instance_ref, RUNNING_run_status_event):
    assert Run.select().where(Run.status == RunStatus.COMPLETED.name, Run.end_time.is_null(False)).count() == 5
    handler = OutOfSequenceInstanceHandler(run_manager_context)
    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[-1].id
    RUNNING_run_status_event.run_id = journey_context.runs[-1].id
    RUNNING_run_status_event.accept(handler)
    assert InstanceAlert.select().count() == 0


@pytest.mark.integration
def test_out_of_sequence_runs_create_alert(
    journey_context, run_manager_context, instance_ref, RUNNING_run_status_event
):
    Run.update({Run.status: RunStatus.RUNNING.name, Run.end_time: None}).where(
        Run.id == journey_context.runs[1].id
    ).execute()
    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[2].id
    RUNNING_run_status_event.run_id = journey_context.runs[2].id
    handler = OutOfSequenceInstanceHandler(run_manager_context)
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.instance.id == journey_context.instance.id
    assert alert.level == AlertLevel.ERROR
    assert alert.type == InstanceAlertType.OUT_OF_SEQUENCE
    assert Instance.select().count() == 1
    instance = Instance.get()
    assert instance.has_warnings is False
    assert instance.has_errors is True
    assert instance.status == InstanceStatus.ERROR.value


@pytest.mark.integration
def test_out_of_sequence_instance_no_started_run_no_alert(journey_context, instance_ref, RUNNING_run_status_event):
    Run.update({Run.status: RunStatus.RUNNING.name, Run.end_time: None}).where(
        Run.id == journey_context.runs[1].id
    ).execute()
    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[2].id
    RUNNING_run_status_event.run_id = journey_context.runs[2].id
    context = RunManagerContext(started_run=False, instances=[instance_ref], component=journey_context.pipelines[2])
    handler = OutOfSequenceInstanceHandler(context)
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 0


@pytest.mark.integration
def test_nonexistent_run_create_alert(journey_context, instance_ref, run_manager_context, RUNNING_run_status_event):
    Run.delete().where(Run.id == journey_context.runs[1].id).execute()
    assert Run.select().count() == 4

    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[2].id
    RUNNING_run_status_event.run_id = journey_context.runs[2].id
    handler = OutOfSequenceInstanceHandler(run_manager_context)
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 1
    alert = InstanceAlert.get()
    assert alert.instance.id == journey_context.instance.id
    assert alert.level == AlertLevel.ERROR
    assert alert.type == InstanceAlertType.OUT_OF_SEQUENCE


@pytest.mark.integration
def test_non_batch_pipeline_upstream_no_alert(
    journey_context, run_manager_context, instance_ref, RUNNING_run_status_event
):
    (
        JourneyDagEdge.update({JourneyDagEdge.left: journey_context.dataset}).where(
            JourneyDagEdge.left == journey_context.pipelines[1]
        )
    ).execute()
    handler = OutOfSequenceInstanceHandler(run_manager_context)
    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[2].id
    RUNNING_run_status_event.run_id = journey_context.runs[2].id
    RUNNING_run_status_event.accept(handler)

    assert (
        JourneyDagEdge.select()
        .where(
            (JourneyDagEdge.left == journey_context.dataset) & (JourneyDagEdge.right == journey_context.pipelines[2])
        )
        .count()
    ) == 1
    assert InstanceAlert.select().count() == 0


@pytest.mark.integration
def test_create_alert_once_per_instance(journey_context, run_manager_context, instance_ref, RUNNING_run_status_event):
    # If the instance already had an out-of-sequence alert, don't create a new one
    (
        Run.update({Run.status: RunStatus.RUNNING.name, Run.end_time: None})
        .where(Run.id.in_([journey_context.runs[0].id, journey_context.runs[1].id]))
        .execute()
    )
    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[1].id
    RUNNING_run_status_event.run_id = journey_context.runs[1].id
    run_manager_context.component = journey_context.pipelines[1]
    handler = OutOfSequenceInstanceHandler(run_manager_context)
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 1

    instance_alert = InstanceAlert.get()
    assert instance_alert.instance.id == journey_context.instance.id

    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[2].id
    RUNNING_run_status_event.run_id = journey_context.runs[2].id
    run_manager_context.component = journey_context.pipelines[2]
    handler = OutOfSequenceInstanceHandler(run_manager_context)
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 1


@pytest.mark.integration
def test_create_alerts_for_multiple_journeys(
    project,
    journey,
    instance,
    pipeline,
    pipeline2,
    simple_dag,
    RUNNING_run_status_event,
):
    Run.create(key="1", pipeline=pipeline, status=RunStatus.RUNNING.name)
    run2 = Run.create(key="2", pipeline=pipeline2, status=RunStatus.RUNNING.name)
    journey2 = Journey.create(name="journey2", project=project)
    JourneyDagEdge.create(journey=journey2, left=pipeline, right=pipeline2)
    instance2 = Instance.create(journey=journey2)
    InstanceSet.get_or_create([instance.id, instance2.id])
    # The same pipelines are used in 2 different journeys -> create 2 alerts for each instance
    RUNNING_run_status_event.pipeline_id = pipeline2.id
    context = RunManagerContext(
        started_run=True,
        run=run2,
        component=pipeline2,
        instances=[InstanceRef(i.journey.id, i.id) for i in [instance, instance2]],
    )

    handler = OutOfSequenceInstanceHandler(context)
    RUNNING_run_status_event.accept(handler)

    # Assert one alert for each instance
    assert InstanceAlert.select().count() == 2
    assert {alert.instance for alert in InstanceAlert.select()} == {instance, instance2}

    # Assert there is one component detail for each instance alert
    instance_alert_components = InstanceAlertsComponents.select()
    assert len(instance_alert_components) == 2
    print([(iac.component_id, pipeline.id) for iac in instance_alert_components])
    assert all(iac.component_id == pipeline.id for iac in instance_alert_components)


@pytest.mark.integration
def test_keep_past_instance_alert_components(
    journey_context, run_manager_context, instance_ref, RUNNING_run_status_event
):
    # Don't delete instance alert component records even if its status changed,
    # e.g. if a pipeline run executed out-of-sequence then finished on the next event, don't need to remove it
    # from the database
    (
        Run.update({Run.status: RunStatus.RUNNING.name, Run.end_time: None})
        .where(Run.id.in_([journey_context.runs[0].id, journey_context.runs[1].id]))
        .execute()
    )

    run_manager_context.component = journey_context.pipelines[1]
    handler = OutOfSequenceInstanceHandler(run_manager_context)

    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[1].id
    RUNNING_run_status_event.run_id = journey_context.runs[1].id
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 1
    assert InstanceAlertsComponents.select().count() == 1
    assert InstanceAlertsComponents.get().component.id == journey_context.pipelines[0].id

    (Run.update({Run.status: RunStatus.COMPLETED.name}).where(Run.id.in_([journey_context.runs[0].id])).execute())

    run_manager_context.component = journey_context.pipelines[2]
    handler = OutOfSequenceInstanceHandler(run_manager_context)

    RUNNING_run_status_event.pipeline_id = journey_context.pipelines[2].id
    RUNNING_run_status_event.run_id = journey_context.runs[2].id
    RUNNING_run_status_event.accept(handler)

    assert InstanceAlert.select().count() == 1
    assert InstanceAlertsComponents.select().count() == 2
    assert {iac.component_id for iac in InstanceAlertsComponents.select()} == {
        journey_context.pipelines[0].id,
        journey_context.pipelines[1].id,
    }
