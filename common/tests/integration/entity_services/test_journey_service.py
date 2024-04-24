from uuid import uuid4

import pytest

from common.entities import Action, Company, Journey, JourneyDagEdge, Rule
from common.entity_services import JourneyService
from common.entity_services.helpers import ComponentFilters, ListRules
from common.exceptions.service import MultipleActionsFound


@pytest.mark.integration
def test_get_rules_with_rules_journey_exists(test_db, journey, rule):
    rules_page = JourneyService.get_rules_with_rules(journey.id, ListRules())
    assert rules_page.total == 1
    assert len(rules_page.results) == 1
    assert rules_page.results[0].id == rule.id


@pytest.mark.integration
def test_get_rules_with_rules_no_pipeline(test_db):
    rules_page = JourneyService.get_rules_with_rules(uuid4(), ListRules())
    assert rules_page.total == 0
    assert len(rules_page.results) == 0


@pytest.mark.integration
def test_get_rules_with_rules_no_rule(test_db, pipeline):
    rules_page = JourneyService.get_rules_with_rules(pipeline.id, ListRules())
    assert rules_page.total == 0
    assert len(rules_page.results) == 0


@pytest.mark.integration
def test_get_rules_with_rules_second_page(test_db, journey, action):
    for _ in range(10):
        Rule.create(journey=journey, rule_schema="some schema", rule_data={}, action=action)
    rules_page = JourneyService.get_rules_with_rules(journey.id, ListRules(page=2, count=6))
    assert rules_page.total == 10
    assert len(rules_page.results) == 4


@pytest.mark.integration
def test_get_action_by_impl_ok(test_db, journey, action):
    ret_action = JourneyService.get_action_by_implementation(journey.id, action.action_impl)
    assert ret_action == action


@pytest.mark.integration
def test_get_action_by_impl_pipeline_not_found(test_db, action):
    ret_action = JourneyService.get_action_by_implementation(uuid4(), action.action_impl)
    assert ret_action is None


@pytest.mark.integration
def test_get_action_by_impl_action_not_found(test_db, journey, action):
    ret_action = JourneyService.get_action_by_implementation(journey.id, action.action_impl + "invalid")
    assert ret_action is None


@pytest.mark.integration
def test_get_action_by_impl_multiple_actions(test_db, journey, action, company):
    Action.create(name="another name", action_impl=action.action_impl, company=company)
    with pytest.raises(MultipleActionsFound):
        JourneyService.get_action_by_implementation(journey.id, action.action_impl)


@pytest.mark.integration
def test_get_action_by_impl_two_actions_on_different_companies(test_db, journey, action, company):
    company2 = Company.create(name="Foo2")
    Action.create(name="A1", company=company2, action_impl=action.action_impl)

    ret_action = JourneyService.get_action_by_implementation(journey.id, action.action_impl)
    assert ret_action == action


@pytest.mark.integration
def test_get_rules_with_rules_no_journey(test_db):
    components_page = JourneyService.get_components_with_rules(str(uuid4()), ListRules(), ComponentFilters())
    assert components_page.total == 0
    assert len(components_page.results) == 0


@pytest.mark.integration
def test_get_component_journey_no_edges(test_db, journey):
    components_page = JourneyService.get_components_with_rules(journey.id, ListRules(), ComponentFilters())
    assert components_page.total == 0
    assert len(components_page.results) == 0


@pytest.mark.integration
def test_get_component_journey_2_edges(test_db, journey, journey_dag_edges, pipeline, pipeline_2, pipeline_3):
    components_page = JourneyService.get_components_with_rules(journey.id, ListRules(), ComponentFilters())
    assert components_page.total == 3
    assert len(components_page.results) == 3
    returned_ids = {components_page.results[i].id for i in range(3)}
    expected_ids = {pipeline.id, pipeline_2.id, pipeline_3.id}
    assert returned_ids == expected_ids


@pytest.mark.integration
def test_get_component_journey_2_edges_search_key(
    test_db, journey, journey_dag_edges, pipeline, pipeline_2, pipeline_3
):
    components_page = JourneyService.get_components_with_rules(journey.id, ListRules(search="1"), ComponentFilters())
    assert components_page.total == 1
    assert len(components_page.results) == 1
    assert components_page.results[0].id == pipeline.id


def create_dag(journey, dag_data):
    for dag in dag_data:
        JourneyDagEdge.create(journey=journey, left=dag["left"], right=dag["right"])
    return list(JourneyDagEdge.select().where(JourneyDagEdge.journey == journey))


@pytest.fixture
def dag1_data(project, pipeline, pipeline_2, pipeline_3):
    """
    Simple sequential DAG:
    -> p1 -> p2 -> p3
    """
    return [
        {"left": None, "right": pipeline},
        {"left": pipeline, "right": pipeline_2},
        {"left": pipeline_2, "right": pipeline_3},
    ]


@pytest.fixture
def dag2_data(project, pipeline, pipeline_2, pipeline_3):
    """
    Multiple siblings DAG:
    -> p1
        | -> p2
        | -> p3
    """
    return [
        {"left": None, "right": pipeline},
        {"left": pipeline, "right": pipeline_2},
        {"left": pipeline, "right": pipeline_3},
    ]


@pytest.fixture
def dag3_data(dataset, project, pipeline, pipeline_2, pipeline_3, pipeline_4):
    """
    More complex DAG:
    -> dataset
        | -> p1
        | -> p2 -> p4
        | -> p3 ---^
        | ---------^
    """
    return [
        {"left": None, "right": dataset},
        {"left": dataset, "right": pipeline},
        {"left": dataset, "right": pipeline_2},
        {"left": dataset, "right": pipeline_3},
        {"left": pipeline_2, "right": pipeline_4},
        {"left": pipeline_3, "right": pipeline_4},
        {"left": dataset, "right": pipeline_4},
    ]


@pytest.mark.integration
@pytest.mark.parametrize(
    "dag_data, expected",
    [
        ("dag1_data", {"P1": [], "P2": [1], "P3": [1, 2]}),
        ("dag2_data", {"P1": [], "P2": [1], "P3": [1]}),
        ("dag3_data", {"D1": [], "P1": [0], "P2": [0], "P3": [0], "P4": [0, 2, 3]}),
    ],
)
def test_get_upstream_nodes(
    dag_data, expected, project, request, dataset, pipeline, pipeline_2, pipeline_3, pipeline_4
):
    components = [dataset, pipeline, pipeline_2, pipeline_3, pipeline_4]
    journey = Journey.create(name="journey-upstream-test", project=project)
    dag = create_dag(journey, request.getfixturevalue(dag_data))
    for node in journey.journey_dag:
        resp = JourneyService.get_upstream_nodes(journey, node.id)
        assert resp == {components[idx].id for idx in expected[node.key]}
