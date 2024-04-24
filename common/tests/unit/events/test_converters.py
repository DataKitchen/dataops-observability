from datetime import datetime
from itertools import product
from uuid import uuid4

import pytest

from common.entities import ApiEventType, RunStatus
from common.events.converters import to_v1, to_v2
from common.events.enums import EventSources
from common.events.v1 import (
    DatasetOperationEvent,
    DatasetOperationType,
    MessageEventLogLevel,
    MessageLogEvent,
    MetricLogEvent,
    RunStatusEvent,
    TestOutcomesEvent,
    TestStatuses,
    instantiate_event_from_data,
)
from common.events.v2 import TestOutcomesUserEvent
from common.events.v2.test_outcomes import (
    TestGenComponentData,
    TestGenDatasetData,
    TestGenTestOutcomeIntegrations,
    TestOutcomeItem,
    TestOutcomeItemIntegrations,
    TestOutcomes,
    TestStatus,
)
from common.events.v2.testgen import (
    TestgenDataset,
    TestgenItem,
    TestgenItemTestParameters,
    TestgenTable,
    TestgenTableGroupV1,
)
from testlib.fixtures.v1_events import *


@pytest.fixture
def base_fields():
    return {
        "source": [EventSources.API.name],
        "event_id": [None, uuid4()],
        "event_timestamp": [str(datetime.now())],
        "received_timestamp": [str(datetime.now())],
        "metadata": [{}, {"a": {"b": "c"}}],
        "external_url": [None, "http://example.com"],
        "component_tool": [None, "MySQL"],
        "payload_keys": [["p1"]],
    }


@pytest.fixture
def id_fields():
    return {
        "project_id": [None, uuid4()],
        "run_id": [None, uuid4()],
        "task_id": [None, uuid4()],
        "run_task_id": [None, uuid4()],
        "instances": [[], [{"journey": uuid4(), "instance": uuid4()}, {"journey": uuid4(), "instance": uuid4()}]],
    }


@pytest.fixture
def component_fields():
    return {
        "batch": {
            "task_name": [None, "a task name"],
            "task_key": [None, "the task key"],
            "run_name": [None, "a run name"],
            "run_key": ["the run key"],
            "pipeline_key": ["the pipeline key"],
            "pipeline_name": [None, "a pipeline name"],
            "pipeline_id": [None, uuid4()],
        },
        "dataset": {
            "dataset_key": ["the dataset key"],
            "dataset_name": [None, "a dataset name"],
            "dataset_id": [None, uuid4()],
        },
        "server": {
            "server_key": ["the server key"],
            "server_name": [None, "a server name"],
            "server_id": [None, uuid4()],
        },
        "stream": {
            "stream_key": ["the stream key"],
            "stream_name": [None, "a stream name"],
            "stream_id": [None, uuid4()],
        },
    }


@pytest.mark.unit
@pytest.mark.slow
def test_convert_run_status_events(base_fields, id_fields, component_fields):
    run_status_fields = {
        "status": [RunStatus.RUNNING.name, RunStatus.PENDING.name],
        "event_type": [RunStatusEvent.__name__],
    }
    all_values = {**base_fields, **id_fields, **component_fields["batch"], **run_status_fields}
    for data in (dict(zip(all_values, v)) for v in product(*all_values.values())):
        event = instantiate_event_from_data(data)
        assert event == to_v1(to_v2(event))


@pytest.mark.unit
@pytest.mark.slow
def test_convert_message_log_events(base_fields, id_fields, component_fields):
    message_log_fields = {
        "log_level": [MessageEventLogLevel.ERROR.name],
        "message": ["test message"],
        "event_type": [MessageLogEvent.__name__],
    }
    for all_values in [
        {**base_fields, **id_fields, **component_field, **message_log_fields}
        for component_field in component_fields.values()
    ]:
        for data in (dict(zip(all_values, v)) for v in product(*all_values.values())):
            event = instantiate_event_from_data(data)
            assert event == to_v1(to_v2(event))


@pytest.mark.unit
@pytest.mark.slow
def test_convert_metric_log_events(base_fields, id_fields, component_fields):
    metric_log_fields = {
        "metric_key": ["some metric key"],
        "metric_value": [0.00000001],
        "event_type": [MetricLogEvent.__name__],
    }
    for all_values in [
        {**base_fields, **id_fields, **component_field, **metric_log_fields}
        for component_field in component_fields.values()
    ]:
        for data in (dict(zip(all_values, v)) for v in product(*all_values.values())):
            event = instantiate_event_from_data(data)
            assert event == to_v1(to_v2(event))


@pytest.mark.unit
@pytest.mark.slow
def test_convert_dataset_operation_event(base_fields, id_fields, component_fields):
    dataset_operation_fields = {
        "operation": [DatasetOperationType.WRITE.name],
        "path": [None, "C:\\Windows\\System32\\System32.dll"],
        "event_type": [DatasetOperationEvent.__name__],
    }
    all_values = {**base_fields, **id_fields, **component_fields["dataset"], **dataset_operation_fields}
    for data in (dict(zip(all_values, v)) for v in product(*all_values.values())):
        event = instantiate_event_from_data(data)
        assert event == to_v1(to_v2(event))


@pytest.mark.unit
@pytest.mark.slow
def test_convert_test_outcomes_events_without_testget(base_fields, id_fields, component_fields):
    test_outcome_fields = {
        "test_outcomes": [
            [
                {
                    "name": "My_test_name0",
                    "status": TestStatuses.WARNING.name,
                    "description": "A description",
                    "start_time": str(datetime.now()),
                    "end_time": None,
                    "metadata": {"key": "value"},
                    "metric_value": 0,
                    "metric_name": None,
                    "metric_description": None,
                    "min_threshold": 0.000001,
                    "max_threshold": 3800000,
                    "integrations": None,
                    "dimensions": None,
                    "result": None,
                    "type": None,
                    "key": None,
                },
            ],
            [
                {
                    "name": "My_test_name1",
                    "status": TestStatuses.PASSED.name,
                    "description": "My description",
                    "start_time": str(datetime.now()),
                    "end_time": str(datetime.now()),
                    "metadata": {1: {2: 3}},
                    "metric_value": 12,
                    "metric_name": "test metric name",
                    "metric_description": "test metric desc",
                    "min_threshold": 25.5,
                    "max_threshold": 38,
                    "integrations": None,
                    "dimensions": ["a", "b"],
                    "result": "test result",
                    "type": "test type",
                    "key": "test key",
                },
                {
                    "name": "My_test_name2",
                    "status": TestStatuses.FAILED.name,
                    "description": None,
                    "start_time": None,
                    "end_time": None,
                    "metadata": {},
                    "metric_value": None,
                    "metric_name": None,
                    "metric_description": None,
                    "min_threshold": None,
                    "max_threshold": None,
                    "integrations": None,
                    "dimensions": None,
                    "result": None,
                    "type": None,
                    "key": None,
                },
            ],
        ],
        "component_integrations": [
            None,
        ],
        "event_type": [TestOutcomesEvent.__name__],
    }
    for all_values in [
        {**base_fields, **id_fields, **component_field, **test_outcome_fields}
        for component_field in component_fields.values()
    ]:
        for data in (dict(zip(all_values, v)) for v in product(*all_values.values())):
            event = instantiate_event_from_data(data)
            assert event == to_v1(to_v2(event))


@pytest.mark.unit
@pytest.mark.slow
def test_convert_test_outcomes_events_with_testgen(base_fields, id_fields, component_fields):
    test_outcome_fields = {
        "test_outcomes": [
            [
                {
                    "name": "My_test_name0",
                    "status": TestStatuses.WARNING.name,
                    "description": "A description",
                    "start_time": str(datetime.now()),
                    "end_time": None,
                    "metadata": {"key": "value"},
                    "metric_value": 0,
                    "metric_name": "test metric name",
                    "metric_description": "test metric desc",
                    "min_threshold": 0.000001,
                    "max_threshold": 3800000,
                    "integrations": {
                        "testgen": {
                            "table": "test table",
                            "test_suite": "test suite",
                            "version": 1,
                            "test_parameters": [],
                            "columns": None,
                        },
                    },
                    "dimensions": ["a", "b"],
                    "result": "test result",
                    "type": "test type",
                    "key": "test key",
                },
            ],
            [
                {
                    "name": "My_test_name1",
                    "status": TestStatuses.PASSED.name,
                    "description": "My description",
                    "start_time": str(datetime.now()),
                    "end_time": str(datetime.now()),
                    "metadata": {1: {2: 3}},
                    "metric_value": 12,
                    "metric_name": "test metric name2",
                    "metric_description": "test metric desc2",
                    "min_threshold": 25.5,
                    "max_threshold": 38,
                    "integrations": {
                        "testgen": {
                            "table": "test table",
                            "test_suite": "test suite",
                            "version": 1,
                            "test_parameters": [
                                {
                                    "name": "test name",
                                    "value": 12.8,
                                },
                                {
                                    "name": "test name2",
                                    "value": "some value",
                                },
                            ],
                            "columns": ["column1", "column2"],
                        },
                    },
                    "dimensions": ["a", "b"],
                    "result": "test result",
                    "type": "test type",
                    "key": "test key",
                },
                {
                    "name": "My_test_name2",
                    "status": TestStatuses.FAILED.name,
                    "description": None,
                    "start_time": None,
                    "end_time": None,
                    "metadata": {},
                    "metric_value": None,
                    "metric_name": None,
                    "metric_description": None,
                    "min_threshold": None,
                    "max_threshold": None,
                    "integrations": {
                        "testgen": {
                            "table": "test table",
                            "test_suite": "test suite",
                            "version": 1,
                            "test_parameters": [],
                            "columns": None,
                        },
                    },
                },
            ],
        ],
        "component_integrations": [
            {
                "integrations": {
                    "testgen": {
                        "version": 1,
                        "database_name": "db test name",
                        "connection_name": "connection test name",
                        "tables": {
                            "include_list": ["item 1", "item 2"],
                            "include_pattern": None,
                            "exclude_pattern": None,
                        },
                        "schema": None,
                        "table_group_configuration": None,
                    },
                },
            },
            {
                "integrations": {
                    "testgen": {
                        "version": 1,
                        "database_name": "db test name2",
                        "connection_name": "connection test name2",
                        "tables": {
                            "include_list": ["item 10", "item 11"],
                            "include_pattern": "test include pattern",
                            "exclude_pattern": "test exclude pattern",
                        },
                        "schema": "test schema",
                        "table_group_configuration": {
                            "group_id": "9663f519-b388-4016-8f70-f67039391d17",
                            "project_code": "test project code",
                            "uses_sampling": False,
                            "sample_percentage": None,
                            "sample_minimum_count": None,
                        },
                    },
                },
            },
            {
                "integrations": {
                    "testgen": {
                        "version": 1,
                        "database_name": "db test name2",
                        "connection_name": "connection test name2",
                        "tables": {
                            "include_list": ["item 10", "item 11"],
                            "include_pattern": "test include pattern2",
                            "exclude_pattern": None,
                        },
                        "schema": None,
                        "table_group_configuration": {
                            "group_id": "9663f519-b388-4016-8f70-f67039391d17",
                            "project_code": "test project code",
                            "uses_sampling": True,
                            "sample_percentage": "test sample %",
                            "sample_minimum_count": 7866,
                        },
                    },
                },
            },
        ],
        "event_type": [TestOutcomesEvent.__name__],
    }
    for all_values in [
        {**base_fields, **id_fields, **component_field, **test_outcome_fields}
        for component_field in component_fields.values()
    ]:
        for data in (dict(zip(all_values, v)) for v in product(*all_values.values())):
            event = instantiate_event_from_data(data)
            assert event == to_v1(to_v2(event))


@pytest.mark.unit
def test_v1_to_v2_convert(test_outcomes_testgen_event):
    v1 = test_outcomes_testgen_event
    item = TestOutcomeItem(
        name=v1.test_outcomes[0].name,
        status=TestStatus[v1.test_outcomes[0].status],
        description=v1.test_outcomes[0].description,
        start_time=v1.test_outcomes[0].start_time,
        end_time=v1.test_outcomes[0].end_time,
        metric_value=v1.test_outcomes[0].metric_value,
        metric_name=v1.test_outcomes[0].metric_name,
        metric_description=v1.test_outcomes[0].metric_description,
        metric_min_threshold=v1.test_outcomes[0].min_threshold,
        metric_max_threshold=v1.test_outcomes[0].max_threshold,
        metadata=v1.test_outcomes[0].metadata,
        dimensions=v1.test_outcomes[0].dimensions,
        result=v1.test_outcomes[0].result,
        type=v1.test_outcomes[0].type,
        key=v1.test_outcomes[0].key,
        integrations=TestOutcomeItemIntegrations(
            testgen=TestgenItem(
                table=v1.test_outcomes[0].integrations.testgen.table,
                test_suite=v1.test_outcomes[0].integrations.testgen.test_suite,
                version=v1.test_outcomes[0].integrations.testgen.version,
                test_parameters=[
                    TestgenItemTestParameters(
                        name=v1.test_outcomes[0].integrations.testgen.test_parameters[0].name,
                        value=v1.test_outcomes[0].integrations.testgen.test_parameters[0].value,
                    ),
                    TestgenItemTestParameters(
                        name=v1.test_outcomes[0].integrations.testgen.test_parameters[1].name,
                        value=v1.test_outcomes[0].integrations.testgen.test_parameters[1].value,
                    ),
                ],
                columns=v1.test_outcomes[0].integrations.testgen.columns,
            )
        ),
    )
    v2 = TestOutcomesUserEvent(
        component_type=v1.component_type,
        created_timestamp=v1.received_timestamp,
        event_id=v1.event_id,
        version=v1.version,
        event_payload=TestOutcomes(
            payload_keys=v1.payload_keys,
            event_timestamp=v1.event_timestamp,
            metadata=v1.metadata,
            external_url=v1.external_url,
            component=TestGenComponentData(
                batch_pipeline=None,
                stream=None,
                dataset=TestGenDatasetData(
                    dataset_key=v1.dataset_key,
                    details=None,
                    integrations=TestGenTestOutcomeIntegrations(
                        testgen=TestgenDataset(
                            version=v1.component_integrations.integrations.testgen.version,
                            database_name=v1.component_integrations.integrations.testgen.database_name,
                            connection_name=v1.component_integrations.integrations.testgen.connection_name,
                            tables=TestgenTable(
                                include_list=v1.component_integrations.integrations.testgen.tables.include_list,
                                include_pattern=v1.component_integrations.integrations.testgen.tables.include_pattern,
                                exclude_pattern=v1.component_integrations.integrations.testgen.tables.exclude_pattern,
                            ),
                            schema=v1.component_integrations.integrations.testgen.schema,
                            table_group_configuration=TestgenTableGroupV1(
                                group_id=v1.component_integrations.integrations.testgen.table_group_configuration.group_id,
                                project_code=v1.component_integrations.integrations.testgen.table_group_configuration.project_code,
                                uses_sampling=v1.component_integrations.integrations.testgen.table_group_configuration.uses_sampling,
                                sample_percentage=v1.component_integrations.integrations.testgen.table_group_configuration.sample_percentage,
                                sample_minimum_count=v1.component_integrations.integrations.testgen.table_group_configuration.sample_minimum_count,
                            ),
                        ),
                    ),
                ),
                server=None,
            ),
            test_outcomes=[item],
        ),
        project_id=v1.project_id,
    )
    assert to_v2(v1) == v2


@pytest.mark.unit
def test_untouched_run_status_event(RUNNING_run_status_event):
    assert id(RUNNING_run_status_event) == id(to_v1(RUNNING_run_status_event))
    v2event = to_v2(RUNNING_run_status_event)
    assert v2event.event_type == ApiEventType.BATCH_PIPELINE_STATUS
    assert id(v2event) == id(to_v2(v2event))


@pytest.mark.unit
def test_untouched_message_log_event(message_log_event):
    assert id(message_log_event) == id(to_v1(message_log_event))
    v2event = to_v2(message_log_event)
    assert v2event.event_type == ApiEventType.MESSAGE_LOG
    assert id(v2event) == id(to_v2(v2event))


@pytest.mark.unit
def test_untouched_metric_log_event(metric_log_event):
    assert id(metric_log_event) == id(to_v1(metric_log_event))
    v2event = to_v2(metric_log_event)
    assert v2event.event_type == ApiEventType.METRIC_LOG
    assert id(v2event) == id(to_v2(v2event))


@pytest.mark.unit
def test_untouched_dataset_operation_event(dataset_operation_event):
    assert id(dataset_operation_event) == id(to_v1(dataset_operation_event))
    v2event = to_v2(dataset_operation_event)
    assert v2event.event_type == ApiEventType.DATASET_OPERATION
    assert id(v2event) == id(to_v2(v2event))


@pytest.mark.unit
def test_untouched_test_outcomes_event(test_outcomes_event):
    assert id(test_outcomes_event) == id(to_v1(test_outcomes_event))
    v2event = to_v2(test_outcomes_event)
    assert v2event.event_type == ApiEventType.TEST_OUTCOMES
    assert id(v2event) == id(to_v2(v2event))
