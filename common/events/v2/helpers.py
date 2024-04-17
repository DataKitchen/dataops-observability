from common.entities import ApiEventType

from .batch_pipeline_status import BatchPipelineStatusSchema
from .dataset_operation import DatasetOperationSchema
from .message_log import MessageLogSchema
from .metric_log import MetricLogSchema
from .test_outcomes import TestOutcomesSchema

EVENT_TYPE_SCHEMAS = {
    ApiEventType.BATCH_PIPELINE_STATUS: BatchPipelineStatusSchema,
    ApiEventType.DATASET_OPERATION: DatasetOperationSchema,
    ApiEventType.MESSAGE_LOG: MessageLogSchema,
    ApiEventType.METRIC_LOG: MetricLogSchema,
    ApiEventType.TEST_OUTCOMES: TestOutcomesSchema,
}
