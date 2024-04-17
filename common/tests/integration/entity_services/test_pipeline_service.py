from uuid import uuid4

import pytest
from peewee import DoesNotExist, IntegrityError

from common.entities import Pipeline, Server
from common.entity_services import PipelineService


@pytest.mark.integration
def test_get_by_key_and_project_nonexistent(test_db):
    with pytest.raises(DoesNotExist):
        PipelineService.get_by_key_and_project("some key", str(uuid4()))


@pytest.mark.integration
def test_get_by_key_and_project_matches_type(test_db, project):
    key = "some key"
    Server.create(key=key, project=project)
    with pytest.raises(DoesNotExist):
        PipelineService.get_by_key_and_project(key, project)

    pipeline = Pipeline.create(key=key, project=project)
    with pytest.raises(IntegrityError):
        Pipeline.create(key=key, project=project)

    result = PipelineService.get_by_key_and_project(key, project)
    assert result == pipeline


@pytest.mark.integration
def test_create_by_name_and_project_error_on_duplicate_name(test_db, project):
    Pipeline.create(key="the key", project=project)
    with pytest.raises(IntegrityError):
        Pipeline.create(key="the key", project=project)


@pytest.mark.integration
def test_get_by_key_and_project_exists(test_db, project, pipeline):
    get_pipeline = PipelineService.get_by_key_and_project(str(pipeline.key), str(project.id))
    assert pipeline == get_pipeline
