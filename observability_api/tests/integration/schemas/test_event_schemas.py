from uuid import UUID

import pytest

from common.entities import Instance, Journey
from common.events.converters import to_v2
from common.events.enums import EventSources
from common.events.v1.run_status_event import ApiRunStatus, RunStatusEvent, RunStatusSchema
from observability_api.schemas.event_schemas import EventResponseSchema
from testlib.fixtures.v2_events import *


@pytest.fixture
def run_status_event(pipeline, project, run, run_task, task):
    v1_event = RunStatusEvent(
        **RunStatusSchema().load(
            {
                "project_id": project.id,
                "event_id": UUID("c86a5696-b3f6-4bf9-94e7-b05883e8e377"),
                "pipeline_id": pipeline.id,
                "run_key": "run-correlation",
                "run_id": run.id,
                "task_key": task.key,
                "task_id": task.id,
                "task_name": task.name,
                "source": EventSources.API.name,
                "pipeline_key": pipeline.key,
                "pipeline_name": pipeline.name,
                "component_tool": pipeline.tool,
                "received_timestamp": "2024-02-02T15:35:08+00:00",
                "event_timestamp": "2024-02-02T15:31:08.425897+00:00",
                "external_url": "https://example.com",
                "run_task_id": run_task.id,
                "metadata": {"key": "value"},
                "event_type": "RunStatusEvent",
                "status": ApiRunStatus.RUNNING.value,
            }
        )
    )
    yield to_v2(v1_event).to_event_entity()


@pytest.mark.integration
def test_event_response_dump(run_status_event, project, pipeline, task, run, run_task, instance):
    # This is usually set by the EventService
    run_status_event.instances = [{"instance": Instance(id=instance.id), "journey": Journey(id=instance.journey_id)}]

    (event_data,) = EventResponseSchema().dump([run_status_event], many=True)

    assert event_data["project"] == {"id": str(project.id)}
    assert len(event_data["components"]) == 1
    assert event_data["components"][0] == {
        "display_name": pipeline.display_name,
        "tool": pipeline.tool,
        "type": pipeline.component_type,
        "id": str(pipeline.id),
        "integrations": [],
    }
    assert event_data["task"] == {
        "display_name": task.display_name,
        "id": str(task.id),
    }
    assert event_data["run"] == {"id": str(run.id)}
    assert event_data["run_task"] == {"id": str(run_task.id)}
    assert event_data["raw_data"] == {
        "batch_pipeline_component": {
            "batch_key": "P1",
            "details": {"name": "Pipe 1", "tool": "TEST_BATCH_PIPELINE_TOOL"},
            "run_key": "run-correlation",
            "run_name": None,
            "task_key": "T1",
            "task_name": "Task 1",
        },
        "event_timestamp": "2024-02-02T15:31:08.425897+00:00",
        "external_url": "https://example.com",
        "metadata": {"key": "value"},
        "payload_keys": [],
        "status": "RUNNING",
    }
    assert event_data["timestamp"] == "2024-02-02T15:31:08.425897+00:00"
    assert event_data["received_timestamp"] == "2024-02-02T15:35:08+00:00"
    assert event_data["id"] == "c86a5696-b3f6-4bf9-94e7-b05883e8e377"
    assert event_data["version"] == 1
    assert event_data["event_type"] == "BATCH_PIPELINE_STATUS"
    assert event_data["instances"] == [
        {"instance": {"id": str(instance.id)}, "journey": {"id": str(instance.journey_id)}}
    ]


@pytest.mark.integration
def test_event_response_dump_defaults(run_status_event, project, pipeline, instance):
    run_status_event.component = None
    run_status_event.run = None
    run_status_event.task = None
    run_status_event.run_task = None
    run_status_event.instance_set = None

    (event_data,) = EventResponseSchema().dump([run_status_event], many=True)

    assert len(event_data["components"]) == 0
    assert event_data["task"] == {
        "display_name": None,
        "id": None,
    }
    assert event_data["run"] == {"id": None}
    assert event_data["run_task"] == {"id": None}
    assert event_data["instances"] == []
