__all__ = [
    "COMPLETED_run_status_event",
    "COMPLETED_run_status_event_data",
    "FAILED_run_status_event",
    "FAILED_run_status_event_data",
    "RUNNING_run_status_event",
    "RUNNING_run_status_event_data",
    "RUNNING_task_status_event",
    "base_events",
    "dataset_key",
    "dataset_operation_event",
    "event_data",
    "message_log_event",
    "message_log_event_data",
    "metadata_model",
    "metric_log_event",
    "metric_log_event_data",
    "pipeline_id",
    "pipeline_key",
    "project_id",
    "run_id",
    "run_key",
    "test_outcome_item_data",
    "test_outcomes_dataset_event",
    "test_outcomes_event",
    "test_outcomes_event_data",
    "test_outcomes_testgen_event",
    "test_outcomes_testgen_event_data",
    "unidentified_event_data",
    "unidentified_event_data_no_keys",
    "valid_event_keys",
]


from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID

import pytest

from common.events.enums import EventSources
from common.events.v1 import (
    ApiRunStatus,
    DatasetOperationEvent,
    DatasetOperationType,
    MessageEventLogLevel,
    MessageLogEvent,
    MetricLogEvent,
    RunStatusEvent,
    TestgenIntegrationVersions,
    TestOutcomesEvent,
    TestStatuses,
)

project_id: UUID = UUID("3a6042d6-41dd-441e-b0bc-a5127a07f04f")
run_id: UUID = UUID("f08b0f0c-d861-44bc-ab60-e3fe8d719bfc")
run_key: str = "run-correlation"
pipeline_id: UUID = UUID("e0ecb1c6-759b-42fe-9641-43454c021ad6")
pipeline_key: str = "aa76735a-7669-4450-97ed-b4107ada4242"
dataset_key: str = "a4328820-654a-4b50-82bd-a568919fb313"

valid_event_keys = ["pipeline_key", "dataset_key", "server_key", "stream_key"]
base_events = ["message_log_event", "test_outcomes_event", "metric_log_event"]


@pytest.fixture
def metadata_model() -> dict[str, str]:
    return {"key": "value"}


@pytest.fixture
def unidentified_event_data_no_keys() -> dict:
    return {
        "external_url": "https://example.com",
        "event_timestamp": "2023-03-30T02:08:22.000042",  # We want this time to be different from received_time
        "metadata": {"key": "value"},
    }


@pytest.fixture
def unidentified_event_data() -> dict:
    return {
        "pipeline_key": pipeline_key,
        "run_key": run_key,
        "external_url": "https://example.com",
        "event_timestamp": "2023-03-30T02:08:22.000042",  # We want this time to be different from received_time
        "metadata": {"key": "value"},
        "component_tool": None,
        "dataset_key": None,
        "dataset_name": None,
        "server_key": None,
        "server_name": None,
        "stream_key": None,
        "stream_name": None,
        "task_key": None,
        "task_name": None,
    }


@pytest.fixture
def event_data():
    return {
        "version": 1,
        "project_id": str(project_id),
        "pipeline_id": str(pipeline_id),
        "run_key": run_key,
        "run_name": None,
        "run_id": str(run_id),
        "task_id": None,
        "task_name": None,
        "task_key": None,
        "event_id": None,
        "external_url": "https://example.com",
        "pipeline_key": pipeline_key,
        "pipeline_name": "pipeline-1",
        "received_timestamp": "2023-03-30T02:08:32.061046",
        "event_timestamp": "2023-03-30T02:08:22.000042",
        "run_task_id": None,
        "metadata": {"key": "value"},
        "instances": [],
        "source": EventSources.API.name,
        "component_tool": None,
        "dataset_id": None,
        "dataset_key": None,
        "dataset_name": None,
        "server_id": None,
        "server_key": None,
        "server_name": None,
        "stream_id": None,
        "stream_key": None,
        "stream_name": None,
        "payload_keys": [],
    }


@pytest.fixture
def message_log_event(event_data):
    data = {
        "event_type": MessageLogEvent.__name__,
        "log_level": MessageEventLogLevel.INFO.name,
        "message": "a log message",
    }
    return MessageLogEvent(**MessageLogEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def message_log_event_data(message_log_event):
    data = message_log_event.as_dict()
    yield data


@pytest.fixture
def metric_log_event(event_data):
    data = {"event_type": MetricLogEvent.__name__, "metric_key": "a group key", "metric_value": 10.0}
    return MetricLogEvent(**MetricLogEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def metric_log_event_data(metric_log_event):
    data = metric_log_event.as_dict()
    yield data


@pytest.fixture
def RUNNING_run_status_event(event_data):
    data = {
        "event_type": RunStatusEvent.__name__,
        "status": ApiRunStatus.RUNNING.name,
    }
    return RunStatusEvent(**RunStatusEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def RUNNING_run_status_event_data(RUNNING_run_status_event):
    data = RUNNING_run_status_event.as_dict()
    yield data


@pytest.fixture
def COMPLETED_run_status_event(event_data):
    data = {
        "event_type": RunStatusEvent.__name__,
        "status": ApiRunStatus.COMPLETED.name,
        "event_timestamp": "2023-03-30T02:08:55.061147",
        "received_timestamp": "2023-03-30T02:08:55.061147",
    }
    return RunStatusEvent(**RunStatusEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def COMPLETED_run_status_event_data(COMPLETED_run_status_event):
    data = COMPLETED_run_status_event.as_dict()
    yield data


@pytest.fixture
def FAILED_run_status_event(event_data):
    data = {
        "event_type": RunStatusEvent.__name__,
        "status": ApiRunStatus.FAILED.name,
    }
    return RunStatusEvent(**RunStatusEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def RUNNING_task_status_event(event_data):
    data = {
        "event_type": RunStatusEvent.__name__,
        "status": ApiRunStatus.RUNNING.name,
        "task_key": "some-task-key",
    }
    return RunStatusEvent(**RunStatusEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def FAILED_run_status_event_data(FAILED_run_status_event):
    data = FAILED_run_status_event.as_dict()
    yield data


@pytest.fixture
def test_outcome_item_data(metadata_model) -> dict:
    timestamp = datetime.now(UTC).isoformat()
    yield {
        "name": "My_test_name",
        "status": TestStatuses.PASSED.name,
        "description": "My description",
        "start_time": timestamp,
        "end_time": timestamp,
        "metric_value": 12,
        "metric_name": "metric_name",
        "metric_description": "metric_description",
        "min_threshold": Decimal(25.5),
        "max_threshold": 38,
        "metadata": metadata_model,
        "dimensions": ["d1", "d2"],
        "result": "ok",
        "type": "type",
        "key": "key",
    }


@pytest.fixture
def test_outcomes_event(event_data, test_outcome_item_data):
    data = {
        "event_type": TestOutcomesEvent.__name__,
        "task_key": "some-task-key",
        "task_name": "some task name",
        "test_outcomes": [test_outcome_item_data],
    }
    return TestOutcomesEvent(**TestOutcomesEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def test_outcomes_dataset_event(event_data, test_outcome_item_data):
    event_data = event_data.copy()
    event_data.pop("pipeline_name")
    event_data.pop("pipeline_id")
    event_data.pop("pipeline_key")
    event_data.pop("run_key")
    data = {
        "dataset_key": dataset_key,
        "event_type": TestOutcomesEvent.__name__,
        "test_outcomes": [test_outcome_item_data],
    }
    return TestOutcomesEvent(**TestOutcomesEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def test_outcomes_testgen_event(event_data, test_outcome_item_data):
    event_data = event_data.copy()
    event_data.pop("pipeline_name")
    event_data.pop("pipeline_id")
    event_data.pop("pipeline_key")
    event_data.pop("run_key")
    event_data.pop("run_id")
    test_outcome_item_data["integrations"] = {
        "testgen": {
            "table": "table1",
            "test_suite": "testsuite1",
            "version": TestgenIntegrationVersions.V1.value,
            "test_parameters": [
                {
                    "name": "parameter1",
                    "value": 3.14,
                },
                {
                    "name": "parameter2",
                    "value": "a string",
                },
            ],
            "columns": ["c1"],
        }
    }
    data = {
        "dataset_key": dataset_key,
        "event_type": TestOutcomesEvent.__name__,
        "test_outcomes": [test_outcome_item_data],
        "component_integrations": {
            "integrations": {
                "testgen": {
                    "version": TestgenIntegrationVersions.V1.value,
                    "database_name": "redshift_db",
                    "connection_name": "redshift_db_con",
                    "tables": {
                        "include_list": ["table1"],
                        "include_pattern": "t.*",
                        "exclude_pattern": ".*private.*",
                    },
                    "schema": "schema1",
                    "table_group_configuration": {
                        "group_id": UUID("9f0fa7b8-8c58-4e5c-ae02-d3cb8504a22e"),
                        "project_code": "topsecretproject",
                        "uses_sampling": True,
                        "sample_percentage": "50.0",
                        "sample_minimum_count": 30,
                    },
                },
            },
        },
    }

    return TestOutcomesEvent(**TestOutcomesEvent.__schema__().load({**event_data, **data}))


@pytest.fixture
def test_outcomes_event_data(test_outcomes_event):
    data = test_outcomes_event.as_dict()
    yield data


@pytest.fixture
def test_outcomes_testgen_event_data(test_outcomes_testgen_event):
    data = test_outcomes_testgen_event.as_dict()
    yield data


@pytest.fixture
def dataset_operation_event(event_data):
    dataset_base = event_data.copy()
    del dataset_base["pipeline_id"]
    del dataset_base["pipeline_name"]
    del dataset_base["pipeline_key"]
    del dataset_base["run_key"]
    del dataset_base["task_key"]
    del dataset_base["task_name"]
    data = {
        "event_type": DatasetOperationEvent.__name__,
        "dataset_key": "55654d75-7e4f-4450-a213-7e7c32ae0566",
        "operation": DatasetOperationType.READ.name,
    }
    return DatasetOperationEvent(**DatasetOperationEvent.__schema__().load({**dataset_base, **data}))
