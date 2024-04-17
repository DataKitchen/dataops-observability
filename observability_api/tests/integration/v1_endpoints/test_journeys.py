from http import HTTPStatus
from uuid import uuid4

import pytest

from common.entities import InstanceRule, InstanceRuleAction, Journey, JourneyDagEdge, Pipeline


@pytest.mark.integration
def test_list_journeys(client, g_user, project, pipeline):
    journey1 = Journey.create(name="Apa", project=project)
    InstanceRule.create(journey=journey1, batch_pipeline=pipeline, action=InstanceRuleAction.START)
    InstanceRule.create(journey=journey1, batch_pipeline=pipeline, action=InstanceRuleAction.START)

    journey2 = Journey.create(name="Bepa", project=project)
    response = client.get(f"/observability/v1/projects/{project.id}/journeys")

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["entities"]) == 2
    assert data["entities"][0]["name"] == journey1.name
    assert len(data["entities"][0]["instance_rules"]) == 2
    assert data["entities"][1]["name"] == journey2.name
    assert len(data["entities"][1]["instance_rules"]) == 0
    assert all(rule["schedule"] is None for j in data["entities"] for rule in j["instance_rules"])


@pytest.mark.integration
def test_list_journeys_forbidden(client, g_user_2, project, pipeline):
    journey1 = Journey.create(name="Apa", project=project)
    InstanceRule.create(journey=journey1, batch_pipeline=pipeline, action=InstanceRuleAction.START)
    InstanceRule.create(journey=journey1, batch_pipeline=pipeline, action=InstanceRuleAction.START)

    _ = Journey.create(name="Bepa", project=project)
    response = client.get(f"/observability/v1/projects/{project.id}/journeys")

    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_list_journeys_name_search(client, g_user, project):
    for i in range(3):
        Journey.create(name=f"P{i}", project=project)

    # Uppercase Search
    search_1 = client.get(f"/observability/v1/projects/{project.id}/journeys", query_string={"search": "P"})
    assert search_1.status_code == HTTPStatus.OK, search_1.json
    data_1 = search_1.json
    assert data_1["total"] == 3
    assert len(data_1["entities"]) == 3
    assert data_1["entities"][0]["name"] in ("P0", "P1", "P2")

    # Lowercase Search
    search_2 = client.get(f"/observability/v1/projects/{project.id}/journeys", query_string={"search": "p"})
    assert search_2.status_code == HTTPStatus.OK, search_2.json
    data_2 = search_2.json
    assert data_2["total"] == 3
    assert len(data_2["entities"]) == 3
    assert data_2["entities"][0]["name"] in ("P0", "P1", "P2")

    # Limited Search
    search_3 = client.get(f"/observability/v1/projects/{project.id}/journeys", query_string={"search": "1"})
    assert search_3.status_code == HTTPStatus.OK, search_3.json
    data_3 = search_3.json
    assert data_3["total"] == 1
    assert len(data_3["entities"]) == 1


@pytest.mark.integration
def test_list_journeys_component_filter(client, g_user, journey, project, components):
    p1, p2, p3, p4, p5 = components
    JourneyDagEdge.create(journey=journey, right=p1)
    JourneyDagEdge.create(journey=journey, left=p1, right=p2)
    JourneyDagEdge.create(journey=journey, left=p1, right=p3)

    # And some unrelated data
    j1 = Journey.create(name="Journey-1", project=project)
    j2 = Journey.create(name="Journey-2", project=project)
    JourneyDagEdge.create(journey=j1, right=p5)
    JourneyDagEdge.create(journey=j2, left=p5, right=p4)

    response = client.get(
        f"/observability/v1/projects/{project.id}/journeys", query_string={"component_id": str(p1.id)}
    )
    assert response.status_code == HTTPStatus.OK, response.json

    data = response.json
    assert data["total"] == 1
    assert data["entities"][0]["id"] == str(journey.id)


@pytest.mark.integration
def test_list_journeys_desc(client, g_user, project):
    journey1 = Journey.create(name="Apa", project=project)
    journey2 = Journey.create(name="Bepa", project=project)
    response = client.get(f"/observability/v1/projects/{project.id}/journeys", query_string={"sort": "desc"})

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["entities"]) == 2
    assert data["entities"][0]["name"] == journey2.name
    assert data["entities"][1]["name"] == journey1.name


@pytest.mark.integration
def test_list_journeys_page_two(client, g_user, project):
    journey1 = Journey.create(name="Apa", project=project)
    journey2 = Journey.create(name="Bepa", project=project)
    response = client.get(f"/observability/v1/projects/{project.id}/journeys", query_string={"page": 2, "count": 1})

    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert "entities" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["entities"]) == 1
    assert data["entities"][0]["name"] in journey2.name


@pytest.mark.integration
def test_list_projects_organization_not_found(client, g_user):
    response = client.get(f"/observability/v1/projects/{uuid4()}/journeys")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_get_journey_by_id(client, g_user, journey):
    response = client.get(f"/observability/v1/journeys/{journey.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(journey.id)
    assert len(data["instance_rules"]) == 0


@pytest.mark.integration
def test_get_journey_by_id_forbidden(client, g_user_2, journey):
    response = client.get(f"/observability/v1/journeys/{journey.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_get_journey_by_id_not_found(client, g_user):
    response = client.get(f"/observability/v1/journeys/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_journey_ok(client, project, g_user):
    req_data = {"name": "Don't Stop Believin'", "description": "journey desc"}
    response = client.post(
        f"/observability/v1/projects/{project.id}/journeys",
        headers={"Content-Type": "application/json"},
        json=req_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    resp_data = response.json
    assert resp_data["id"] is not None
    assert resp_data["name"] == req_data["name"]
    assert resp_data["description"] == req_data["description"]
    assert resp_data["project"] == str(project.id)
    assert resp_data["created_by"]["id"] == str(g_user.id)
    assert resp_data["created_on"] is not None
    assert len(Journey.select().where(Journey.name == req_data["name"]).execute()) == 1


@pytest.mark.integration
def test_post_journey_forbidden(client, project, g_user_2):
    req_data = {"name": "Don't Stop Believin'", "description": "journey desc"}
    response = client.post(
        f"/observability/v1/projects/{project.id}/journeys",
        headers={"Content-Type": "application/json"},
        json=req_data,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_post_journey_project_not_found(client, g_user):
    response = client.post(
        f"/observability/v1/projects/{uuid4()}/journeys",
        headers={"Content-Type": "application/json"},
        json={},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_journey_duplicate_key(client, project, journey, g_user):
    response = client.post(
        f"/observability/v1/projects/{project.id}/journeys",
        headers={"Content-Type": "application/json"},
        json={"name": journey.name},
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json


@pytest.mark.integration
def test_post_journey_default_description(client, project, g_user):
    response = client.post(
        f"/observability/v1/projects/{project.id}/journeys",
        headers={"Content-Type": "application/json"},
        json={"name": "a journey name"},
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    resp_data = response.json
    assert resp_data["description"] is None


@pytest.mark.integration
def test_post_journey_invalid_field(client, project, g_user):
    response = client.post(
        f"/observability/v1/projects/{project.id}/journeys",
        headers={"Content-Type": "application/json"},
        json={"invalid_field": "a data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
@pytest.mark.parametrize(["description", "name"], [("new description!", None), (None, "New name")])
def test_patch_journey_ok(client, g_user, journey, description, name):
    new_data = {
        "name": name,
        "description": description,
    }
    response = client.patch(
        f"/observability/v1/journeys/{journey.id}",
        headers={"Content-Type": "application/json"},
        json=new_data,
    )
    assert response.status_code == HTTPStatus.OK, response.json
    resp_data = response.json
    assert resp_data["id"] == str(journey.id)
    assert resp_data["name"] == new_data["name"]
    assert resp_data["description"] == new_data["description"]


@pytest.mark.integration
def test_patch_journey_forbidden(client, g_user_2, journey):
    new_data = {
        "name": "My Name",
        "description": "My Description",
    }
    response = client.patch(
        f"/observability/v1/journeys/{journey.id}",
        headers={"Content-Type": "application/json"},
        json=new_data,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_patch_journey_not_found(client, g_user):
    response = client.patch(
        f"/observability/v1/journeys/{uuid4()}",
        headers={"Content-Type": "application/json"},
        json={"name": "this is a new name"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_patch_journey_invalid_field(client, journey, g_user):
    response = client.patch(
        f"/observability/v1/journeys/{journey.id}",
        headers={"Content-Type": "application/json"},
        json={"invalid field": "data"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_journey_duplicate_name(client, g_user, project, journey):
    journey2 = Journey.create(name="Foo2", project=project)
    response = client.patch(
        f"/observability/v1/journeys/{journey2.id}",
        headers={"Content-Type": "application/json"},
        json={"name": journey.name},
    )
    assert response.status_code == HTTPStatus.CONFLICT, response.json


@pytest.mark.integration
def test_delete_journey_ok(client, g_user, journey, dag_edges):
    assert len(Journey.select()) == 1
    response = client.delete(f"/observability/v1/journeys/{journey.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert len(Journey.select()) == 0


@pytest.mark.integration
def test_delete_journey_forbidden(client, g_user_2, journey):
    response = client.delete(f"/observability/v1/journeys/{journey.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_delete_journey_not_found(client, g_user, journey):
    assert len(Journey.select()) == 1
    response = client.delete(f"/observability/v1/journeys/{uuid4()}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert len(Journey.select()) == 1


@pytest.fixture
def components(project):
    batch_pipe_1 = Pipeline.create(key="Batch-Pipeline-1", project=project)
    batch_pipe_2 = Pipeline.create(key="Batch-Pipeline-2", project=project)
    batch_pipe_3 = Pipeline.create(key="Batch-Pipeline-3", project=project)
    batch_pipe_4 = Pipeline.create(key="Batch-Pipeline-4", project=project)
    batch_pipe_5 = Pipeline.create(key="Batch-Pipeline-5", project=project)
    return (batch_pipe_1, batch_pipe_2, batch_pipe_3, batch_pipe_4, batch_pipe_5)


@pytest.fixture
def dag_edges(journey, components):
    p1, p2, p3, p4, p5 = components
    edge_1 = JourneyDagEdge.create(journey=journey, right=p1)
    edge_2 = JourneyDagEdge.create(journey=journey, left=p1, right=p2)
    edge_3 = JourneyDagEdge.create(journey=journey, left=p1, right=p3)
    edge_4 = JourneyDagEdge.create(journey=journey, left=p2, right=p3)
    edge_5 = JourneyDagEdge.create(journey=journey, left=p3, right=p4)
    edge_6 = JourneyDagEdge.create(journey=journey, left=p3, right=p5)
    return (edge_1, edge_2, edge_3, edge_4, edge_5, edge_6)


@pytest.mark.integration
def test_get_journey_dag(client, g_user, dag_edges, components, journey):
    response = client.get(f"/observability/v1/journeys/{journey.id}/dag")
    assert response.status_code == HTTPStatus.OK
    data = response.json
    p1, p2, p3, p4, p5 = components

    assert len(data["nodes"]) == len(components)
    assert len([edges for node in data["nodes"] for edges in node["edges"]]) == len(dag_edges)

    expected_edges = (
        ([str(dag_edges[0].id)], []),
        ([str(dag_edges[1].id)], [str(p1.id)]),
        ([str(dag_edges[3].id), str(dag_edges[2].id)], [str(p1.id), str(p2.id)]),
        ([str(dag_edges[4].id)], [str(p3.id)]),
        ([str(dag_edges[5].id)], [str(p3.id)]),
    )

    for node, expected_node, expected_edge in zip(
        sorted(data["nodes"], key=lambda x: x["component"]["key"]), components, expected_edges
    ):
        assert node["component"]["id"] == str(expected_node.id)
        for edge in node["edges"]:
            assert edge["id"] in expected_edge[0]
            if expected_edge[1]:
                assert edge["component"] in expected_edge[1]
            else:
                assert edge["component"] is None


@pytest.mark.integration
def test_get_journey_dag_journey_not_found(client, g_user):
    response = client.get(f"/observability/v1/journeys/{uuid4()}/dag")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_get_journey_dag_no_extras(client, g_user, dag_edges, components, journey, project, user):
    # Create some extra data in the same project
    j2 = Journey.create(name="J2", project=project, created_by=user.id)
    c1 = Pipeline.create(key="Component M", project=project)
    c2 = Pipeline.create(key="Component N", project=project)
    e1 = JourneyDagEdge.create(journey=j2, right=c1)

    response = client.get(f"/observability/v1/journeys/{journey.id}/dag")
    assert response.status_code == HTTPStatus.OK

    # The unrelated pipelines should not be returned
    node_ids = [str(node["component"]["id"]) for node in response.json["nodes"]]
    assert str(c1.id) not in node_ids
    assert str(c2.id) not in node_ids

    # Unrelated edges should not be returned
    edge_ids = [str(edge["id"]) for node in response.json["nodes"] for edge in node["edges"]]
    assert str(e1.id) not in edge_ids


@pytest.mark.integration
def test_get_journey_dag_loose_components(client, g_user, project, user):
    # Create a journey with multiple loose components
    journey = Journey.create(name="Some Journey", project=project, created_by=user.id)
    component1 = Pipeline.create(key="Component 1", project=project)
    component2 = Pipeline.create(key="Component 2", project=project)
    edge1 = JourneyDagEdge.create(journey=journey, right=component1)
    edge2 = JourneyDagEdge.create(journey=journey, right=component2)

    response = client.get(f"/observability/v1/journeys/{journey.id}/dag")
    assert response.status_code == HTTPStatus.OK

    node_ids = [str(node["component"]["id"]) for node in response.json["nodes"]]
    assert len(node_ids) == 2
    assert sorted(node_ids) == sorted([str(component1.id), str(component2.id)])

    edge_ids = [edge["id"] for node in response.json["nodes"] for edge in node["edges"]]
    assert len(edge_ids) == 2
    assert sorted(edge_ids) == sorted([str(edge1.id), str(edge2.id)])


@pytest.mark.integration
def test_get_journey_dag_forbidden(client, journey, g_user_2):
    response = client.get(f"/observability/v1/journeys/{journey.id}/dag")
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.integration
def test_get_journey_dag_forbidden_2(client, journey):
    response = client.get(f"/observability/v1/journeys/{journey.id}/dag")
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.integration
def test_create_dag_edge(client, g_user, journey, components):
    p1, _, p3, _, _ = components

    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": p1.id, "right": p3.id},
    )
    assert response.status_code == HTTPStatus.CREATED

    # Response should include the following keys
    assert {"journey", "id", "left", "right"} == set(response.json.keys())


@pytest.mark.integration
def test_create_dag_edge_forbidden(client, g_user_2, journey, components):
    p1, _, p3, _, _ = components

    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": p1.id, "right": p3.id},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json


@pytest.mark.integration
def test_create_dag_edge_forbidden_2(client, journey):
    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": "", "right": ""},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.integration
def test_create_dag_edge_journey_not_found(client, g_user, journey):
    response = client.put(
        "/observability/v1/journeys/682ffa11-baca-4fb7-b0c6-250e1978f579/dag",
        headers={"Content-Type": "application/json"},
        json={"left": "682ffa11-baca-4fb7-b0c6-250e1978f579", "right": "18059d82-d001-4b08-9d5d-d5f2d72ac26b"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_create_dag_edge_edge_not_found(client, g_user, journey, components):
    _, _, p3, _, _ = components
    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": "69bb9898-2b0a-420b-9563-5425152894d4", "right": p3.id},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_create_dag_edge_edge_not_found_2(client, g_user, journey, components):
    p1, _, _, _, _ = components
    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": p1.id, "right": "18059d82-d001-4b08-9d5d-d5f2d72ac26b"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.integration
def test_create_dag_edge_right_only(client, g_user, journey, components):
    _, _, p3, _, _ = components

    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"right": p3.id},
    )
    assert response.status_code == HTTPStatus.CREATED

    # Response should include the following keys
    assert {"journey", "id", "left", "right"} == set(response.json.keys())


@pytest.mark.integration
def test_create_dag_edge_cycle_error(client, g_user, journey, components, dag_edges):
    p1, _, _, p4, _ = components
    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": p4.id, "right": p1.id},
    )
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.integration
def test_create_dag_edge_duplicate_fail(client, g_user, journey, components, dag_edges):
    p1, p2, _, _, _ = components
    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={"left": p1.id, "right": p2.id},
    )
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.integration
def test_create_dag_edge_no_relationship_fail(client, g_user, journey, components, dag_edges):
    """Creating a DAG edge should fail if both relationships are missing."""
    p1, p2, _, _, _ = components

    response = client.put(
        f"/observability/v1/journeys/{journey.id}/dag",
        headers={"Content-Type": "application/json"},
        json={},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.integration
def test_dag_edge_delete(client, g_user, dag_edges):
    edge_count = JourneyDagEdge.select().count()
    e1 = dag_edges[0]
    response = client.delete(f"/observability/v1/journey-dag-edge/{e1.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert JourneyDagEdge.select().count() == edge_count - 1


@pytest.mark.integration
def test_dag_edge_delete_already_deleted(client, g_user, dag_edges):
    """No error should be raised when a dag edge has already been deleted or does not exist."""
    response = client.delete("/observability/v1/journey-dag-edge/7165abc3-c340-4abe-8c13-d2aaca0c0fb2")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json


@pytest.mark.integration
def test_dag_edge_delete_forbidden(client, g_user_2, dag_edges):
    edge_count = JourneyDagEdge.select().count()
    e1 = dag_edges[0]
    response = client.delete(f"/observability/v1/journey-dag-edge/{e1.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert JourneyDagEdge.select().count() == edge_count
