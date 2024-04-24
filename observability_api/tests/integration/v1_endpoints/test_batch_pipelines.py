from dataclasses import dataclass
from http import HTTPStatus
from uuid import uuid4

import pytest

from common.entities import Organization, Pipeline, Project, User


@dataclass
class PipelineCtx:
    project: Project
    pipeline: Pipeline
    user: User


@pytest.fixture
def pipeline_ctx(g_user, company) -> PipelineCtx:
    org = Organization.create(name="Foo", company=company)
    proj = Project.create(name="Foo", active=True, organization=org)
    pipeline = Pipeline.create(key="Foo", name="P1", description="Description.", project=proj, created_by=g_user.id)
    return PipelineCtx(proj, pipeline, g_user)


@pytest.mark.integration
def test_get_batch_pipeline_by_id(client, pipeline_ctx):
    response = client.get(f"/observability/v1/batch-pipelines/{pipeline_ctx.pipeline.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(pipeline_ctx.pipeline.id)
    assert data["created_on"] is not None
    assert data["created_by"]["id"] == str(pipeline_ctx.user.id)


@pytest.mark.integration
def test_get_batch_pipeline_by_id_not_found(client, g_user):
    response = client.get(f"/observability/v1/batch-pipelines/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_pipeline_ok(client, pipeline_ctx, g_user):
    req_data = {"key": "pipe key", "description": "pipe desc"}
    response = client.post(
        f"/observability/v1/projects/{pipeline_ctx.project.id}/batch-pipelines",
        headers={"Content-Type": "application/json"},
        json=req_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    resp_data = response.json
    assert resp_data["id"] is not None
    assert resp_data["key"] == req_data["key"]
    assert resp_data["description"] == req_data["description"]
    assert resp_data["project"] == str(pipeline_ctx.project.id)
    assert len(Pipeline.select().where(Pipeline.key == req_data["key"]).execute()) == 1
    assert resp_data["created_on"] is not None
    assert resp_data["created_by"]["id"] == str(g_user.id)


@pytest.mark.integration
def test_post_batch_pipeline_project_not_found(client, g_user):
    response = client.post(
        f"/observability/v1/projects/{uuid4()}/batch-pipelines",
        headers={"Content-Type": "application/json"},
        json={"key": "a pipe key"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_pipeline_duplicate_key(client, pipeline_ctx):
    response = client.post(
        f"/observability/v1/projects/{pipeline_ctx.project.id}/batch-pipelines",
        headers={"Content-Type": "application/json"},
        json={"key": pipeline_ctx.pipeline.key},
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json


@pytest.mark.integration
def test_post_pipeline_default_description(client, pipeline_ctx):
    response = client.post(
        f"/observability/v1/projects/{pipeline_ctx.project.id}/batch-pipelines",
        headers={"Content-Type": "application/json"},
        json={"key": "a pipe key"},
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    resp_data = response.json
    assert resp_data["description"] is None


@pytest.mark.integration
def test_post_pipeline_invalid_field(client, pipeline_ctx):
    response = client.post(
        f"/observability/v1/projects/{pipeline_ctx.project.id}/batch-pipelines",
        headers={"Content-Type": "application/json"},
        json={"invalid_field": "a data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
@pytest.mark.parametrize(["description", "name"], [("New Description", "new-name"), (None, None)])
def test_patch_pipeline_ok(client, pipeline_ctx, description, name):
    new_data = {
        "key": "this is a new key",
        "name": name,
        "description": description,
        "labels": {"another label": "with data"},
    }
    response = client.patch(
        f"/observability/v1/batch-pipelines/{pipeline_ctx.pipeline.id}",
        headers={"Content-Type": "application/json"},
        json=new_data,
    )
    assert response.status_code == HTTPStatus.OK, response.json
    resp_data = response.json
    assert resp_data["id"] == str(pipeline_ctx.pipeline.id)
    assert resp_data["key"] == new_data["key"]
    assert resp_data["name"] == new_data["name"]
    assert resp_data["description"] == new_data["description"]
    assert resp_data["labels"] == new_data["labels"]


@pytest.mark.integration
def test_patch_pipeline_not_found(client, pipeline_ctx):
    response = client.patch(
        f"/observability/v1/batch-pipelines/{uuid4()}",
        headers={"Content-Type": "application/json"},
        json={"key": "this is a new key"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_patch_pipeline_invalid_field(client, pipeline_ctx):
    response = client.patch(
        f"/observability/v1/batch-pipelines/{pipeline_ctx.pipeline.id}",
        headers={"Content-Type": "application/json"},
        json={"invalid field": "data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_pipeline_duplicate_key(client, pipeline_ctx):
    pipeline2 = Pipeline.create(key="Foo2", project=pipeline_ctx.project)
    response = client.patch(
        f"/observability/v1/batch-pipelines/{pipeline2.id}",
        headers={"Content-Type": "application/json"},
        json={"key": pipeline_ctx.pipeline.key},
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json
