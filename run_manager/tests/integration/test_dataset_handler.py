import pytest

from common.entities import DatasetOperation
from run_manager.context import RunManagerContext
from run_manager.event_handlers import DatasetHandler


@pytest.mark.integration
def test_dataset_handler_insert_operation(dataset_operation_event, dataset, instance_instance_set):
    handler = DatasetHandler(RunManagerContext(component=dataset, instance_set=instance_instance_set.instance_set))

    assert DatasetOperation.select().count() == 0

    ret = handler.handle_dataset_operation(dataset_operation_event)

    assert ret is True
    assert DatasetOperation.select().count() == 1
    dataset_operation = DatasetOperation.select().get()
    assert dataset_operation.dataset == dataset
    assert dataset_operation.instance_set.iis.count() == 1
