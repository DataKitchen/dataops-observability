import pytest

from common.events.v2 import BatchPipelineData, ComponentData, DatasetData


@pytest.fixture
def default_base_payload_dict():
    return {"external_url": None, "event_timestamp": None, "metadata": {}, "payload_keys": []}


@pytest.fixture
def batch_pipeline_dict():
    return {
        "batch_key": "batch key",
        "run_key": "run key",
    }


@pytest.fixture
def component_data_dict(batch_pipeline_dict):
    return {"batch_pipeline": batch_pipeline_dict}


@pytest.fixture
def default_batch_pipeline_data(batch_pipeline_dict):
    return BatchPipelineData(
        batch_key=batch_pipeline_dict["batch_key"],
        run_key=batch_pipeline_dict["run_key"],
        run_name=None,
        task_key=None,
        task_name=None,
        details=None,
    )


@pytest.fixture
def dataset_dict():
    return {
        "dataset_key": "dataset key",
    }


@pytest.fixture
def default_dataset_data(dataset_dict):
    return DatasetData(
        dataset_key=dataset_dict["dataset_key"],
        details=None,
    )


@pytest.fixture
def default_component_data(batch_pipeline_dict):
    return ComponentData(
        batch_pipeline=BatchPipelineData(
            batch_key=batch_pipeline_dict["batch_key"],
            run_key=batch_pipeline_dict["run_key"],
            run_name=None,
            task_key=None,
            task_name=None,
            details=None,
        ),
        dataset=None,
        server=None,
        stream=None,
    )
