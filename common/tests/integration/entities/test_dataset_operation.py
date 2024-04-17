from datetime import datetime

import pytest

from common.entities import DatasetOperation, DatasetOperationType


@pytest.mark.integration
def test_dataset_operation_create(dataset, instance_set):
    DatasetOperation.create(
        dataset=dataset,
        instance_set=instance_set,
        operation=DatasetOperationType.WRITE,
        operation_time=datetime.utcnow(),
    )
