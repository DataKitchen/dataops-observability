import pytest
from marshmallow.exceptions import ValidationError

from common.entities import RunStatus
from common.events.v2 import BatchPipelineStatus, BatchPipelineStatusSchema


@pytest.mark.unit
def test_run_status_invalid(batch_pipeline_dict):
    with pytest.raises(ValidationError, match="status"):
        BatchPipelineStatusSchema().load({"batch_pipeline_component": batch_pipeline_dict})

    with pytest.raises(ValidationError, match="Must be one of"):
        BatchPipelineStatusSchema().load(
            # Testing with an internal status to check that the API doesn't accept them
            {"status": RunStatus.PENDING.name, "batch_pipeline_component": batch_pipeline_dict}
        )


@pytest.mark.unit
def test_run_status_valid(default_batch_pipeline_data, batch_pipeline_dict, default_base_payload_dict):
    assert BatchPipelineStatusSchema().load(
        {"status": RunStatus.RUNNING.name, "batch_pipeline_component": batch_pipeline_dict}
    ) == BatchPipelineStatus(
        status=RunStatus.RUNNING, batch_pipeline_component=default_batch_pipeline_data, **default_base_payload_dict
    )
