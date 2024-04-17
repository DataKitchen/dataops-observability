__all__ = ["DatasetHandler"]
import logging

from common.entities.dataset_operation import DatasetOperation
from common.events import EventHandlerBase
from common.events.v1 import DatasetOperationEvent
from run_manager.context import RunManagerContext

LOG = logging.getLogger(__name__)


class DatasetHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context

    def handle_dataset_operation(self, event: DatasetOperationEvent) -> bool:
        dso = DatasetOperation.create(
            dataset=self.context.component,
            instance_set=self.context.instance_set,
            operation_time=event.event_timestamp,
            operation=event.operation,
            path=event.path,
        )
        LOG.info("Created %s", dso)
        return True
