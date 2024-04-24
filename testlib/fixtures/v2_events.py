__all__ = [
    "BATCH_PIPELINE_STATUS_EVENT_ID",
    "CREATED_TIMESTAMP",
    "EVENT_TIMESTAMP",
    "INSTANCE_ALERT_EVENT_ID",
    "LOG_EVENT_ID",
    "RUNNING_batch_status_event_v2",
    "RUNNING_batch_status_payload",
    "RUNNING_batch_status_platform_event_v2",
    "RUN_ALERT_EVENT_ID",
    "batch_pipeline_data",
    "dataset_operation_event_v2",
    "instance_alert",
    "message_log_event_v2",
    "metadata_model",
    "metric_log_event_v2",
    "run_alert",
    "test_outcome_item",
    "test_outcomes_testgen_event_v2",
]

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

import pytest

from common.entities import AlertLevel, InstanceAlertType, RunAlertType, RunStatus
from common.entities.event import ApiEventType
from common.events.base import InstanceRef
from common.events.internal import BatchPipelineStatusPlatformEvent
from common.events.internal.alert import InstanceAlert, RunAlert
from common.events.v2 import (
    BatchPipelineData,
    BatchPipelineStatus,
    BatchPipelineStatusUserEvent,
    ComponentData,
    DatasetData,
    DatasetOperation,
    DatasetOperationType,
    DatasetOperationUserEvent,
    LogEntry,
    LogLevel,
    MessageLog,
    MessageLogUserEvent,
    MetricEntry,
    MetricLog,
    MetricLogUserEvent,
    TestGenComponentData,
    TestGenDatasetData,
    TestGenTestOutcomeIntegrations,
    TestOutcomeItem,
    TestOutcomeItemIntegrations,
    TestOutcomes,
    TestOutcomesUserEvent,
    TestStatus,
)
from common.events.v2.testgen import (
    TestgenDataset,
    TestgenIntegrationVersions,
    TestgenItem,
    TestgenItemTestParameters,
    TestgenTable,
    TestgenTableGroupV1,
)

from .entities import (
    DATASET_ID,
    INSTANCE_ALERT_ID,
    INSTANCE_ID,
    JOURNEY_ID,
    PIPELINE_ID,
    PROJECT_ID,
    RUN_ALERT_ID,
    RUN_ID,
)

LOG_EVENT_ID: UUID = UUID("3421ba9a-e090-4e52-9cd3-6723a5553a56")
"""ID for EventV2 LOG event."""

BATCH_PIPELINE_STATUS_EVENT_ID: UUID = UUID("10f1eb1a-c63b-47d3-9239-e44d7bb5d071")
"""ID for EventV2 BATCH PIPELINE STATUS event."""

TEST_OUTCOMES_EVENT_ID: UUID = UUID("83af84bc-318e-4dda-9d40-6c7c8bacd992")
"""ID for EventV2 LOG event."""

EVENT_TIMESTAMP: datetime = datetime(2023, 5, 10, 1, 1, 1, tzinfo=timezone.utc)
"""Default timestamp for events."""

CREATED_TIMESTAMP: datetime = EVENT_TIMESTAMP + timedelta(minutes=3, seconds=1)
"""Default timestamp at which an event is actually created (always a few mins later than the event timestamp)"""

INSTANCE_ALERT_EVENT_ID: UUID = UUID("df0202d2-8e5e-4e8b-94fb-fef65992675d")
"""Event ID for InstanceAlert event."""

RUN_ALERT_EVENT_ID: UUID = UUID("ee794eec-ff64-4443-aefa-df544b95ffbf")
"""Event ID for RunAlert event."""

DATASET_KEY: str = "Ae9lWtkYNJaxg3h"


@pytest.fixture
def metadata_model() -> dict[str, str]:
    return {"key": "value"}


@pytest.fixture
def batch_pipeline_data():
    return BatchPipelineData(
        batch_key="batch key",
        run_key="run key",
        run_name=None,
        task_key=None,
        task_name=None,
        details=None,
    )


@pytest.fixture
def message_log_event_v2() -> MessageLogUserEvent:
    payload = MessageLog(
        event_timestamp=EVENT_TIMESTAMP,
        metadata={},
        external_url=None,
        payload_keys=["p1", "p2"],
        component=ComponentData(batch_pipeline=None, stream=None, dataset=None, server=None),
        log_entries=[
            LogEntry(level=LogLevel.INFO, message="GOOD"),
            LogEntry(level=LogLevel.WARNING, message="BAD"),
        ],
    )
    return MessageLogUserEvent(
        created_timestamp=CREATED_TIMESTAMP,
        event_id=LOG_EVENT_ID,
        event_payload=payload,
        event_type=ApiEventType.MESSAGE_LOG,
        project_id=PROJECT_ID,
    )


@pytest.fixture
def metric_log_event_v2() -> MetricLogUserEvent:
    payload = MetricLog(
        event_timestamp=EVENT_TIMESTAMP,
        metadata={},
        external_url=None,
        payload_keys=["p1", "p2"],
        component=ComponentData(batch_pipeline=None, stream=None, dataset=None, server=None),
        metric_entries=[
            MetricEntry(key="metric-log-key-1", value=Decimal("0.5")),
            MetricEntry(key="metric-log-key-2", value=Decimal("3.42")),
        ],
    )
    return MetricLogUserEvent(
        created_timestamp=CREATED_TIMESTAMP,
        event_id=LOG_EVENT_ID,
        event_payload=payload,
        event_type=ApiEventType.METRIC_LOG,
        project_id=PROJECT_ID,
    )


@pytest.fixture
def instance_alert() -> InstanceAlert:
    return InstanceAlert(
        event_id=INSTANCE_ALERT_EVENT_ID,
        created_timestamp=CREATED_TIMESTAMP,
        alert_id=INSTANCE_ALERT_ID,
        description="A test instance alert",
        level=AlertLevel.WARNING,
        journey_id=JOURNEY_ID,
        project_id=PROJECT_ID,
        type=InstanceAlertType.INCOMPLETE,
    )


@pytest.fixture
def run_alert() -> RunAlert:
    return RunAlert(
        event_id=RUN_ALERT_EVENT_ID,
        run_id=RUN_ID,
        created_timestamp=CREATED_TIMESTAMP,
        description="A test run alert",
        alert_id=RUN_ALERT_ID,
        level=AlertLevel.WARNING,
        batch_pipeline_id=PIPELINE_ID,
        project_id=PROJECT_ID,
        type=RunAlertType.LATE_START,
    )


@pytest.fixture
def test_outcome_item(metadata_model) -> TestOutcomeItem:
    timestamp = datetime.now(timezone.utc)
    return TestOutcomeItem(
        name="My_test_name",
        status=TestStatus.PASSED,
        description="My description",
        start_time=timestamp,
        end_time=timestamp,
        metric_value=Decimal(12),
        metric_name="metric_name",
        metric_description="metric_description",
        metric_min_threshold=Decimal(25.5),
        metric_max_threshold=Decimal(38),
        metadata=metadata_model,
        integrations=None,
        dimensions=["d1", "d2"],
        result="ok",
        type="type",
        key="key",
    )


@pytest.fixture
def test_outcomes_testgen_event_v2(test_outcome_item):
    test_outcome_item.integrations = TestOutcomeItemIntegrations(
        testgen=TestgenItem(
            table="table1",
            test_suite="testsuite1",
            version=TestgenIntegrationVersions.V1,
            test_parameters=[
                TestgenItemTestParameters(
                    name="parameter1",
                    value=Decimal(3.14),
                ),
                TestgenItemTestParameters(
                    name="parameter2",
                    value="a string",
                ),
            ],
            columns=["c1"],
        )
    )
    payload = TestOutcomes(
        event_timestamp=EVENT_TIMESTAMP,
        metadata={},
        external_url=None,
        payload_keys=["p1", "p2"],
        component=TestGenComponentData(
            batch_pipeline=None,
            stream=None,
            dataset=TestGenDatasetData(
                dataset_key=DATASET_KEY,
                details=None,
                integrations=TestGenTestOutcomeIntegrations(
                    testgen=TestgenDataset(
                        version=TestgenIntegrationVersions.V1,
                        database_name="redshift_db",
                        connection_name="redshift_db_con",
                        tables=TestgenTable(
                            include_list=["table1"],
                            include_pattern="t.*",
                            exclude_pattern=".*private.*",
                        ),
                        schema="schema1",
                        table_group_configuration=TestgenTableGroupV1(
                            group_id=UUID("9f0fa7b8-8c58-4e5c-ae02-d3cb8504a22e"),
                            project_code="topsecretproject",
                            uses_sampling=True,
                            sample_percentage="50.0",
                            sample_minimum_count=30,
                        ),
                    ),
                ),
            ),
            server=None,
        ),
        test_outcomes=[test_outcome_item],
    )
    return TestOutcomesUserEvent(
        created_timestamp=CREATED_TIMESTAMP,
        event_id=TEST_OUTCOMES_EVENT_ID,
        event_payload=payload,
        project_id=PROJECT_ID,
    )


@pytest.fixture
def RUNNING_batch_status_payload(batch_pipeline_data):
    return BatchPipelineStatus(
        event_timestamp=EVENT_TIMESTAMP,
        metadata={},
        external_url=None,
        batch_pipeline_component=batch_pipeline_data,
        status=RunStatus.RUNNING,
        payload_keys=[],
    )


@pytest.fixture
def RUNNING_batch_status_event_v2(RUNNING_batch_status_payload):
    return BatchPipelineStatusUserEvent(
        created_timestamp=CREATED_TIMESTAMP,
        event_id=BATCH_PIPELINE_STATUS_EVENT_ID,
        event_payload=RUNNING_batch_status_payload,
        project_id=PROJECT_ID,
        component_id=PIPELINE_ID,
        run_id=RUN_ID,
    )


@pytest.fixture
def RUNNING_batch_status_platform_event_v2(RUNNING_batch_status_payload):
    return BatchPipelineStatusPlatformEvent(
        created_timestamp=CREATED_TIMESTAMP,
        event_id=BATCH_PIPELINE_STATUS_EVENT_ID,
        event_payload=RUNNING_batch_status_payload,
        project_id=PROJECT_ID,
        component_id=PIPELINE_ID,
        run_id=RUN_ID,
    )


@pytest.fixture
def dataset_operation_event_v2():
    payload = DatasetOperation(
        event_timestamp=EVENT_TIMESTAMP,
        metadata={},
        external_url=None,
        dataset_component=DatasetData(
            dataset_key="dataset key",
            details=None,
        ),
        operation=DatasetOperationType.WRITE,
        path="some/path/to/file",
        payload_keys=[],
    )
    return DatasetOperationUserEvent(
        created_timestamp=CREATED_TIMESTAMP,
        event_id=BATCH_PIPELINE_STATUS_EVENT_ID,
        event_payload=payload,
        project_id=PROJECT_ID,
        component_id=DATASET_ID,
        instances=[InstanceRef(journey_id=JOURNEY_ID, instance_id=INSTANCE_ID)],
    )
