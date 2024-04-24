__all__ = ["NORMALIZED_TO_V1_EVENT_TYPE", "V1_TO_NORMALIZED_EVENT_TYPE"]

from common.entities.event import ApiEventType
from common.events.v1.dataset_operation_event import DatasetOperationEvent
from common.events.v1.message_log_event import MessageLogEvent
from common.events.v1.metric_log_event import MetricLogEvent
from common.events.v1.run_status_event import RunStatusEvent
from common.events.v1.test_outcomes_event import TestOutcomesEvent

V1_TO_NORMALIZED_EVENT_TYPE: dict[str, ApiEventType] = {
    RunStatusEvent.__name__: ApiEventType.BATCH_PIPELINE_STATUS,
    DatasetOperationEvent.__name__: ApiEventType.DATASET_OPERATION,
    MessageLogEvent.__name__: ApiEventType.MESSAGE_LOG,
    MetricLogEvent.__name__: ApiEventType.METRIC_LOG,
    TestOutcomesEvent.__name__: ApiEventType.TEST_OUTCOMES,
}
NORMALIZED_TO_V1_EVENT_TYPE: dict[str, str] = {v.name: k for k, v in V1_TO_NORMALIZED_EVENT_TYPE.items()}
