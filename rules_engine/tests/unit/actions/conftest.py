from datetime import datetime
from unittest.mock import Mock

import pytest

from common.entities import Action
from common.events.enums import EventSources
from common.events.v1 import ApiRunStatus, RunStatusEvent
from testlib.fixtures.entities import rule  # noqa: F401
from testlib.fixtures.v1_events import *


@pytest.fixture
def run_status_event():
    data = {
        "event_timestamp": "2022-11-29 05:05:59.061084+00:00",
        "event_type": RunStatusEvent.__name__,
        "external_url": "https://example.com",
        "pipeline_id": "bfee8e76-0985-4f27-bdae-f8c3a178655b",
        "pipeline_key": "60871e66-f491-4456-9467-694fad33a029",
        "pipeline_name": "My Pipeline",
        "project_id": "f94b31e9-9963-47c2-b9c5-8ad5dc2a4068",
        "received_timestamp": "2022-11-29 05:06:06.741457+00:00",
        "source": EventSources.API.name,
        "task_id": "a5d80c67-c6d1-42f8-bd53-0f46324f8cd5",
        "task_key": "a task key",
        "status": ApiRunStatus.RUNNING.name,
        "metadata": {},
        "run_id": "ab0bc9f1-7db0-4ecf-b1ef-342529bd9918",
        "run_key": "a run key",
        "run_name": "a run name",
        "run_task_id": None,
    }
    status_event = RunStatusEvent(**RunStatusEvent.__schema__().load(data))
    status_event.project = Mock()
    status_event.project.name = "a project name"
    status_event.run_task = Mock()
    status_event.run_task.start_time = datetime.utcnow()
    status_event.component = Mock()
    status_event.component.display_name = "test component name"
    status_event.task = Mock()
    status_event.task.display_name = "test task name"
    return status_event


@pytest.fixture
def mocked_test_outcomes_dataset_event(test_outcomes_dataset_event):
    test_outcomes_dataset_event.project = Mock()
    test_outcomes_dataset_event.project.name = "a project name"
    test_outcomes_dataset_event.run_task = Mock()
    test_outcomes_dataset_event.run_task.start_time = datetime.utcnow()
    test_outcomes_dataset_event.component = Mock()
    test_outcomes_dataset_event.component.display_name = "test component name"
    test_outcomes_dataset_event.task = Mock()
    test_outcomes_dataset_event.task.display_name = "test task name"
    return test_outcomes_dataset_event


@pytest.fixture
def action():
    action = Action(name="action1", action_impl="fake")
    yield action
