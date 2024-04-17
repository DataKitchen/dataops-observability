from http import HTTPStatus
from typing import Type
from uuid import UUID, uuid4

import pytest
from werkzeug.datastructures import MultiDict

from common.entities import BaseEntity, Component, ComponentType, JourneyDagEdge
from common.schemas.fields import strip_upper_underscore

subcomponent_test_params = pytest.mark.parametrize(
    "route, subcomponent",
    [
        ("batch-pipelines", "pipeline"),
        ("datasets", "dataset"),
        ("servers", "server"),
        ("streaming-pipelines", "streaming-pipeline"),
    ],
    indirect=["subcomponent"],
)


@pytest.mark.integration
def test_list_components(client, project, pipeline, g_user):
    test_tool = "test tool"
    component_2 = Component.create(
        type=ComponentType.BATCH_PIPELINE.name, key="Bar", project=project.id, created_by=g_user.id, tool=test_tool
    )

    response = client.get(f"/observability/v1/projects/{project.id}/components")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["entities"]) == 2
    assert data["entities"][0]["key"] == component_2.key
    assert data["entities"][1]["key"] == pipeline.key
    assert "created_by" in data["entities"][0]
    assert "created_on" in data["entities"][0]
    assert data["entities"][0]["created_by"]["id"] == str(g_user.id)
    assert data["entities"][0]["type"] == ComponentType.BATCH_PIPELINE.value
    assert data["entities"][0]["tool"] == strip_upper_underscore(test_tool)


@pytest.mark.integration
def test_list_components_testgen_component(client, project, dataset, testgen_dataset_component, g_user):
    response = client.get(f"/observability/v1/projects/{project.id}/components")
    data = response.json
    assert data["total"] == 1
    testgen_components = data["entities"][0]["integrations"]
    assert 1 == len(testgen_components)

    testgen_component = testgen_components[0]
    assert testgen_dataset_component.id == UUID(testgen_component["id"])
    assert testgen_dataset_component.database_name == testgen_component["database_name"]
    assert testgen_dataset_component.connection_name == testgen_component["connection_name"]
    assert testgen_dataset_component.schema == testgen_component["schema"]
    assert testgen_dataset_component.table_list == testgen_component["table_list"]
    assert testgen_dataset_component.table_group_id == testgen_component["table_group_id"]
    assert testgen_dataset_component.project_code == testgen_component["project_code"]


@pytest.mark.integration
def test_list_components_key_search(client, project, g_user):
    components = [
        Component.create(type=ComponentType.BATCH_PIPELINE.name, key="P0", project=project),
        Component.create(type=ComponentType.BATCH_PIPELINE.name, key="Key1", name="P1", project=project),
        Component.create(type=ComponentType.BATCH_PIPELINE.name, key="P2", project=project),
    ]

    # Uppercase Search (Can be searched by name or key)
    search_1 = client.get(f"/observability/v1/projects/{project.id}/components", query_string={"search": "P"})
    assert search_1.status_code == HTTPStatus.OK, search_1.json
    data_1 = search_1.json
    assert data_1["total"] == 3
    assert len(data_1["entities"]) == 3
    for idx, component in enumerate(components):
        assert data_1["entities"][idx]["display_name"] == component.display_name

    # Lowercase Search
    search_2 = client.get(f"/observability/v1/projects/{project.id}/components", query_string={"search": "p"})
    assert search_2.status_code == HTTPStatus.OK, search_2.json
    data_2 = search_2.json
    assert data_2["total"] == 3
    assert len(data_2["entities"]) == 3
    for idx, component in enumerate(components):
        assert data_1["entities"][idx]["display_name"] == component.display_name

    # Limited Search
    search_3 = client.get(f"/observability/v1/projects/{project.id}/components", query_string={"search": "1"})
    assert search_3.status_code == HTTPStatus.OK, search_3.json
    data_3 = search_3.json
    assert data_3["total"] == 1
    assert len(data_3["entities"]) == 1


@pytest.mark.integration
def test_list_components_sort(client, project, g_user):
    alpha = Component.create(type=ComponentType.BATCH_PIPELINE.name, key="alpha_000", project=project)
    beta = Component.create(type=ComponentType.BATCH_PIPELINE.name, key="beta_000", name="testing", project=project)
    delta = Component.create(type=ComponentType.BATCH_PIPELINE.name, key="delta_000", project=project)

    # Sort by display_name and key
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string={"search": "_000"})

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["total"] == 3
    assert len(data["entities"]) == 3
    assert data["entities"][0]["key"] == alpha.key
    # delta came before beta because sorting by name is prioritized over key
    assert data["entities"][1]["key"] == delta.key
    assert data["entities"][2]["key"] == beta.key

    component_1 = Component.create(type=ComponentType.BATCH_PIPELINE.name, key="foo", name="Abc_sort", project=project)
    component_2 = Component.create(type=ComponentType.BATCH_PIPELINE.name, key="bar", name="Xyz_sort", project=project)

    # Sort ASC by default
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string={"search": "_sort"})

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 2
    assert data["entities"][0]["key"] == component_1.key
    assert data["entities"][1]["key"] == component_2.key

    # Sort DESC
    response = client.get(
        f"/observability/v1/projects/{project.id}/components",
        query_string={"search": "_sort", "sort": "desc"},
    )
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["entities"][0]["key"] == component_2.key
    assert data["entities"][1]["key"] == component_1.key


@pytest.mark.integration
def test_list_components_page_two(client, project, pipeline, g_user):
    Component.create(type=ComponentType.BATCH_PIPELINE.name, key="Bar", project=project)
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string={"page": 2, "count": 1})

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["entities"]) == 1
    assert data["entities"][0]["key"] == pipeline.key


@pytest.mark.integration
def test_list_components_filter(client, project, pipeline, g_user):
    dataset = Component.create(type=ComponentType.DATASET.name, key="Qoo2", project=project)

    # Base case: no filter
    response = client.get(f"/observability/v1/projects/{project.id}/components")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 2
    assert data["entities"][0]["key"] == pipeline.key
    assert data["entities"][1]["key"] == dataset.key

    # Filter by component_type
    qs = MultiDict([("component_type", ComponentType.BATCH_PIPELINE.name)])
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 1
    assert data["entities"][0]["key"] == pipeline.key

    # Invalid component_type
    qs = MultiDict([("component_type", "INVALID_COMPONENT_TYPE")])
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_list_components_filter_tool(client, project, pipeline, dataset, server, g_user):
    # Base case: no filter
    response = client.get(f"/observability/v1/projects/{project.id}/components")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 3

    # Filter by one tool
    qs = MultiDict([("tool", pipeline.tool.lower())])
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 1
    assert data["entities"][0]["id"] == str(pipeline.id)

    # Filter by two tools
    qs = MultiDict([("tool", pipeline.tool.lower()), ("tool", dataset.tool)])
    response = client.get(f"/observability/v1/projects/{project.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 2
    assert str(pipeline.id) in [c["id"] for c in data["entities"]]
    assert str(dataset.id) in [c["id"] for c in data["entities"]]


@pytest.mark.integration
def test_list_components_when_projects_not_found(client, pipeline, g_user):
    response = client.get(f"/observability/v1/projects/{uuid4()}/components")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_components_when_projects_forbidden(client, project, pipeline, g_user_2):
    response = client.get(f"/observability/v1/projects/{project.id}/components")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_components_when_projects_admin(client, project, pipeline, g_user_2_admin):
    response = client.get(f"/observability/v1/projects/{project.id}/components")
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
def test_get_component_by_id(client, pipeline, g_user):
    response = client.get(f"/observability/v1/components/{pipeline.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(pipeline.id)
    assert data["type"] == ComponentType.BATCH_PIPELINE.value


@pytest.mark.integration
def test_get_component_by_id_with_testgen_components(client, dataset, testgen_dataset_component, g_user):
    response = client.get(f"/observability/v1/components/{dataset.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    testgen_components = response.json["integrations"]
    assert 1 == len(testgen_components)

    testgen_component = testgen_components[0]
    assert testgen_dataset_component.id == UUID(testgen_component["id"])
    assert dataset.id == UUID(testgen_component["component"])


@pytest.mark.integration
def test_get_component_by_id_not_found(client, g_user):
    response = client.get(f"/observability/v1/components/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_get_component_by_id_forbidden(client, pipeline, g_user_2):
    response = client.get(f"/observability/v1/components/{pipeline.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_component_by_id_admin(client, pipeline, g_user_2_admin):
    response = client.get(f"/observability/v1/components/{pipeline.id}")
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
def test_delete_component_ok(client, pipeline, g_user):
    response = client.delete(f"/observability/v1/components/{pipeline.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert len(Component.select()) == 0


@pytest.mark.integration
def test_delete_component_not_found(client, pipeline, g_user):
    uuid = uuid4()
    response = client.delete(f"/observability/v1/components/{uuid}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert len(Component.select()) == 1


@pytest.mark.integration
def test_delete_component_forbidden(client, pipeline, g_user_2):
    response = client.delete(f"/observability/v1/components/{pipeline.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert len(Component.select()) == 1


@pytest.mark.integration
def test_delete_component_admin(client, pipeline, g_user_2_admin):
    response = client.delete(f"/observability/v1/components/{pipeline.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert len(Component.select()) == 0


@pytest.mark.integration
def test_get_component_from_journey(client, journey, journey_dag_edge, pipeline, g_user):
    response = client.get(f"/observability/v1/journeys/{journey.id}/components")
    assert response.status_code == HTTPStatus.OK, response.json
    component = response.json["entities"][0]
    assert component["id"] == str(pipeline.id)
    assert component["display_name"] == pipeline.display_name
    assert component["type"] == ComponentType.BATCH_PIPELINE.value


@pytest.mark.integration
def test_get_component_from_journey_component_type_filter(client, journey, journey_dag_edge, pipeline, g_user, project):
    dataset = Component.create(type=ComponentType.DATASET.name, key="Qoo2", project=project)
    _ = JourneyDagEdge.create(journey=journey, left=None, right=dataset)

    # Base case: no filter
    response = client.get(f"/observability/v1/journeys/{journey.id}/components")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 2, response.json
    assert [(c["display_name"], c["type"]) for c in response.json["entities"]] == [
        (pipeline.name, ComponentType.BATCH_PIPELINE.name),
        (dataset.key, ComponentType.DATASET.name),
    ]

    # Filter by component_type
    qs = MultiDict([("component_type", ComponentType.DATASET.name)])
    response = client.get(f"/observability/v1/journeys/{journey.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 1, response.json
    component = response.json["entities"][0]
    assert component["display_name"] == dataset.display_name
    assert component["type"] == ComponentType.DATASET.value


@pytest.mark.integration
def test_get_component_from_journey_component_tool_filter(client, journey, pipeline, dataset, stream, g_user):
    JourneyDagEdge.insert_many(
        [{"journey": journey, "left": None, "right": component} for component in [pipeline, dataset, stream]]
    ).execute()

    # Base case: no filter
    response = client.get(f"/observability/v1/journeys/{journey.id}/components")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 3

    # Filter by a tool
    qs = MultiDict([("tool", dataset.tool)])
    response = client.get(f"/observability/v1/journeys/{journey.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 1
    assert data["entities"][0]["id"] == str(dataset.id)

    # Filter by two tools
    qs = MultiDict([("tool", stream.tool.lower()), ("tool", pipeline.tool)])
    response = client.get(f"/observability/v1/journeys/{journey.id}/components", query_string=qs)
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert len(data["entities"]) == 2
    assert str(stream.id) in [c["id"] for c in data["entities"]]
    assert str(pipeline.id) in [c["id"] for c in data["entities"]]


@pytest.mark.integration
def test_get_component_from_journey_not_exist(client, journey, journey_dag_edge, pipeline, g_user):
    response = client.get(f"/observability/v1/journeys/{uuid4()}/components")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_get_component_from_journey_forbidden(client, journey, journey_dag_edge, pipeline, g_user_2):
    response = client.get(f"/observability/v1/journeys/{journey.id}/components")
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.integration
def test_get_component_from_journey_admin(client, journey, journey_dag_edge, pipeline, g_user_2_admin):
    response = client.get(f"/observability/v1/journeys/{journey.id}/components")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json["entities"]) == 1


@pytest.mark.integration
def test_get_component_from_journey_with_key(client, journey, journey_dag_edge, pipeline, g_user):
    response = client.get(f"/observability/v1/journeys/{journey.id}/components?search={pipeline.key[1:2]}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 1, response.json
    component = response.json["entities"][0]
    assert component["id"] == str(pipeline.id)
    assert component["display_name"] == pipeline.display_name
    assert component["type"] == ComponentType.BATCH_PIPELINE.value


@pytest.mark.integration
def test_get_component_from_journey_with_key_no_results(client, journey, g_user):
    response = client.get(f"/observability/v1/journeys/{journey.id}/components?search=bar")
    assert response.status_code == HTTPStatus.OK, response.json
    assert len(response.json["entities"]) == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "route, component_type",
    [
        ("batch-pipelines", ComponentType.BATCH_PIPELINE.value),
        ("datasets", ComponentType.DATASET.value),
        ("servers", ComponentType.SERVER.value),
        ("streaming-pipelines", ComponentType.STREAMING_PIPELINE.value),
    ],
)
def test_post_subcomponent_ok(route, component_type, client, project, g_user):
    req_data = {"key": "pipe key", "description": "pipe desc", "tool": "a_b"}
    response = client.post(
        f"/observability/v1/projects/{project.id}/{route}",
        headers={"Content-Type": "application/json"},
        json=req_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    resp_data = response.json
    assert resp_data["id"] is not None
    assert resp_data["key"] == req_data["key"]
    assert resp_data["description"] == req_data["description"]
    assert resp_data["tool"] == strip_upper_underscore(req_data["tool"])
    assert resp_data["project"] == str(project.id)
    assert (
        Component.select().where((Component.key == req_data["key"]) & (Component.type == component_type)).count() == 1
    )
    assert resp_data["created_on"] is not None
    assert resp_data["created_by"]["id"] == str(g_user.id)


@pytest.mark.integration
@subcomponent_test_params
def test_post_subcomponent_project_not_found(route, subcomponent, client, project, g_user):
    response = client.post(
        f"/observability/v1/projects/{uuid4()}/{route}",
        headers={"Content-Type": "application/json"},
        json={"key": "a pipe key"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_post_subcomponent_duplicate_key(route, subcomponent: Type[BaseEntity], client, project, g_user):
    response = client.post(
        f"/observability/v1/projects/{project.id}/{route}",
        headers={"Content-Type": "application/json"},
        json={"key": subcomponent.key},
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_post_subcomponent_default_description(route, subcomponent, client, project, g_user):
    response = client.post(
        f"/observability/v1/projects/{project.id}/{route}",
        headers={"Content-Type": "application/json"},
        json={"key": "a pipe key"},
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    resp_data = response.json
    assert resp_data["description"] is None


@pytest.mark.integration
@subcomponent_test_params
def test_post_subcomponent_invalid_field(route, subcomponent, client, project, g_user):
    response = client.post(
        f"/observability/v1/projects/{project.id}/{route}",
        headers={"Content-Type": "application/json"},
        json={"invalid_field": "a data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_post_subcomponent_forbidden(route, subcomponent, client, project, g_user_2):
    response = client.post(
        f"/observability/v1/projects/{project.id}/{route}",
        headers={"Content-Type": "application/json"},
        json={"key": "a new key"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_post_subcomponent_admin(route, subcomponent, client, project, g_user_2_admin):
    response = client.post(
        f"/observability/v1/projects/{project.id}/{route}",
        headers={"Content-Type": "application/json"},
        json={"key": "a new key"},
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert response.json["created_by"]["id"] == str(g_user_2_admin.user.id)


@pytest.mark.integration
def test_post_subcomponent_invalid_tool(client, project, g_user):
    req_data = {"key": "pipe key", "tool": "_!#¤_"}
    response = client.post(
        f"/observability/v1/projects/{project.id}/batch-pipelines",
        headers={"Content-Type": "application/json"},
        json=req_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    assert "tool" in response.json["error"]


@pytest.mark.integration
@subcomponent_test_params
def test_get_subcomponent_by_id(route, subcomponent: Type[BaseEntity], client, g_user):
    response = client.get(f"/observability/v1/{route}/{subcomponent.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(subcomponent.id)
    assert data["created_on"] is not None
    assert data["created_by"]["id"] == str(g_user.id)


@pytest.mark.integration
@subcomponent_test_params
def test_get_subcomponent_by_id_forbidden(route, subcomponent: Type[BaseEntity], client, g_user_2):
    response = client.get(f"/observability/v1/{route}/{subcomponent.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_get_subcomponent_by_id_admin(route, subcomponent: Type[BaseEntity], client, g_user_2_admin):
    response = client.get(f"/observability/v1/{route}/{subcomponent.id}")
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_ok(route, subcomponent: Type[BaseEntity], client, g_user):
    new_data = {
        "key": "this is a new key",
        "name": "some new name",
        "tool": "some new tool",
        "labels": {"another label": "with data"},
    }
    response = client.patch(
        f"/observability/v1/{route}/{subcomponent.id}",
        headers={"Content-Type": "application/json"},
        json=new_data,
    )
    assert response.status_code == HTTPStatus.OK, response.json
    resp_data = response.json
    assert resp_data["id"] == str(subcomponent.id)
    assert resp_data["key"] == new_data["key"]
    assert resp_data["name"] == new_data["name"]
    assert resp_data["tool"] == strip_upper_underscore(new_data["tool"])
    assert resp_data["description"] == subcomponent.description
    assert resp_data["labels"] == new_data["labels"]


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_clear_fields(route, subcomponent: Type[BaseEntity], client, g_user):
    new_data = {
        "name": None,
        "tool": None,
        "labels": {},
    }
    response = client.patch(
        f"/observability/v1/{route}/{subcomponent.id}",
        headers={"Content-Type": "application/json"},
        json=new_data,
    )
    assert response.status_code == HTTPStatus.OK, response.json
    resp_data = response.json
    assert resp_data["id"] == str(subcomponent.id)
    assert resp_data["name"] == new_data["name"]
    assert resp_data["tool"] == new_data["name"]
    assert resp_data["labels"] == new_data["labels"]


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_not_found(route, subcomponent, client, pipeline, g_user):
    response = client.patch(
        f"/observability/v1/{route}/{uuid4()}",
        headers={"Content-Type": "application/json"},
        json={"key": "this is a new key"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_forbidden(route, subcomponent: Type[BaseEntity], client, pipeline, g_user_2):
    response = client.patch(
        f"/observability/v1/{route}/{subcomponent.id}",
        headers={"Content-Type": "application/json"},
        json={"key": "this is a new key"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_admin(route, subcomponent: Type[BaseEntity], client, pipeline, g_user_2_admin):
    response = client.patch(
        f"/observability/v1/{route}/{subcomponent.id}",
        headers={"Content-Type": "application/json"},
        json={"key": "this is a new key"},
    )
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_invalid_field(route, subcomponent: Type[BaseEntity], client, pipeline, g_user):
    response = client.patch(
        f"/observability/v1/{route}/{subcomponent.id}",
        headers={"Content-Type": "application/json"},
        json={"invalid field": "data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
@subcomponent_test_params
def test_patch_subcomponent_duplicate_key(route, subcomponent: Type[BaseEntity], client, project, g_user):
    component2 = Component.create(key="Foo2", project=project, type=subcomponent.type)
    response = client.patch(
        f"/observability/v1/{route}/{component2.id}",
        headers={"Content-Type": "application/json"},
        json={"key": subcomponent.key},
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json
