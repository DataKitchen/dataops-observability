from uuid import uuid4

import pytest

from common.entities import Action, ActionImpl, Company, Journey, JourneyDagEdge, Rule
from common.entity_services import JourneyService
from common.entity_services.helpers import ComponentFilters, ListRules
from common.exceptions.service import MultipleActionsFound


# --- parse_patterns ---


@pytest.mark.unit
def test_parse_patterns_none():
    assert JourneyService.parse_patterns(None) == []


@pytest.mark.unit
def test_parse_patterns_empty_string():
    assert JourneyService.parse_patterns("") == []


@pytest.mark.unit
def test_parse_patterns_comma_separated():
    assert JourneyService.parse_patterns("a,b,c") == ["a", "b", "c"]


@pytest.mark.unit
def test_parse_patterns_newline_separated():
    assert JourneyService.parse_patterns("a\nb\nc") == ["a", "b", "c"]


@pytest.mark.unit
def test_parse_patterns_trims_whitespace():
    assert JourneyService.parse_patterns("  a  ,  b  ") == ["a", "b"]


@pytest.mark.unit
def test_parse_patterns_skips_empty_entries():
    assert JourneyService.parse_patterns("a,,b") == ["a", "b"]


# --- get_components_matching_patterns ---


@pytest.mark.integration
def test_get_components_matching_patterns_no_include_returns_empty(test_db, project, pipeline, pipeline_2):
    result = JourneyService.get_components_matching_patterns(str(project.id), [], [])
    assert result == []


@pytest.mark.integration
def test_get_components_matching_patterns_wildcard_matches_all(test_db, project, pipeline, pipeline_2):
    result = JourneyService.get_components_matching_patterns(str(project.id), ["*"], [])
    assert {c.id for c in result} == {pipeline.id, pipeline_2.id}


@pytest.mark.integration
def test_get_components_matching_patterns_exact_key(test_db, project, pipeline, pipeline_2):
    result = JourneyService.get_components_matching_patterns(str(project.id), ["P1"], [])
    assert len(result) == 1
    assert result[0].id == pipeline.id


@pytest.mark.integration
def test_get_components_matching_patterns_exclude_applied(test_db, project, pipeline, pipeline_2):
    result = JourneyService.get_components_matching_patterns(str(project.id), ["*"], ["P2"])
    assert len(result) == 1
    assert result[0].id == pipeline.id


@pytest.mark.integration
def test_get_components_matching_patterns_character_class_matches(test_db, project, pipeline, pipeline_2):
    # [pP]* matches both P1 and P2 regardless of case
    result = JourneyService.get_components_matching_patterns(str(project.id), ["[pP]*"], [])
    assert {c.id for c in result} == {pipeline.id, pipeline_2.id}


@pytest.mark.integration
def test_get_components_matching_patterns_character_class_negation(test_db, project, pipeline, pipeline_2):
    # [!pP]* excludes keys starting with p or P — neither P1 nor P2 should match
    result = JourneyService.get_components_matching_patterns(str(project.id), ["[!pP]*"], [])
    assert result == []


@pytest.mark.integration
def test_get_components_matching_patterns_character_class_exclude(test_db, project, pipeline, pipeline_2):
    # include all, but exclude keys starting with p or P
    result = JourneyService.get_components_matching_patterns(str(project.id), ["*"], ["[pP]*"])
    assert result == []


@pytest.mark.integration
def test_get_components_matching_patterns_character_class_exclude_negation(test_db, project, pipeline, pipeline_2):
    # exclude *[!1] matches keys not ending in '1' — P2 is excluded, P1 remains
    result = JourneyService.get_components_matching_patterns(str(project.id), ["*"], ["*[!1]"])
    assert len(result) == 1
    assert result[0].id == pipeline.id


@pytest.mark.integration
def test_get_components_matching_patterns_question_mark_matches_any_single_char(test_db, project, pipeline, pipeline_2):
    # P? matches any key of exactly two chars starting with P — both P1 and P2 match
    result = JourneyService.get_components_matching_patterns(str(project.id), ["P?"], [])
    assert {c.id for c in result} == {pipeline.id, pipeline_2.id}


@pytest.mark.integration
def test_get_components_matching_patterns_question_mark_matches_specific(test_db, project, pipeline, pipeline_2):
    # ?1 matches any two-char key ending in '1' — only P1 matches
    result = JourneyService.get_components_matching_patterns(str(project.id), ["?1"], [])
    assert len(result) == 1
    assert result[0].id == pipeline.id


@pytest.mark.integration
def test_get_components_matching_patterns_question_mark_exclude(test_db, project, pipeline, pipeline_2):
    # exclude ?1 removes P1, leaving P2
    result = JourneyService.get_components_matching_patterns(str(project.id), ["*"], ["?1"])
    assert len(result) == 1
    assert result[0].id == pipeline_2.id


@pytest.mark.integration
def test_get_components_matching_patterns_only_own_project(test_db, project, pipeline, organization, user):
    from common.entities import Pipeline, Project

    other_project = Project.create(name="Other", organization=organization, created_by=user)
    Pipeline.create(name="Other P1", key="P1", project=other_project, created_by=user)
    result = JourneyService.get_components_matching_patterns(str(project.id), ["P1"], [])
    assert len(result) == 1
    assert result[0].id == pipeline.id


# --- apply_component_patterns ---


@pytest.mark.integration
def test_apply_component_patterns_no_include_clears_edges(test_db, journey, pipeline):
    JourneyDagEdge.create(journey=journey, left=None, right=pipeline)
    journey.component_include_patterns = None
    journey.component_exclude_patterns = None
    JourneyService.apply_component_patterns(journey)
    assert JourneyDagEdge.select().where(JourneyDagEdge.journey == journey).count() == 0


@pytest.mark.integration
def test_apply_component_patterns_adds_matching_as_root_nodes(test_db, journey, pipeline, pipeline_2):
    journey.component_include_patterns = "*"
    journey.component_exclude_patterns = None
    JourneyService.apply_component_patterns(journey)
    edges = list(JourneyDagEdge.select().where(JourneyDagEdge.journey == journey))
    assert len(edges) == 2
    assert all(e.left_id is None for e in edges)


@pytest.mark.integration
def test_apply_component_patterns_preserves_existing_edges(test_db, journey, pipeline, pipeline_2):
    JourneyDagEdge.create(journey=journey, left=pipeline, right=pipeline_2)
    journey.component_include_patterns = "*"
    journey.component_exclude_patterns = None
    JourneyService.apply_component_patterns(journey)
    edges = list(JourneyDagEdge.select().where(JourneyDagEdge.journey == journey))
    # pipeline is root (no predecessor); pipeline->pipeline_2 edge is restored; pipeline_2 gets no root entry
    assert len(edges) == 2
    root_edges = [e for e in edges if e.left_id is None]
    assert len(root_edges) == 1
    assert root_edges[0].right_id == pipeline.id


@pytest.mark.integration
def test_apply_component_patterns_drops_edge_when_component_excluded(test_db, journey, pipeline, pipeline_2):
    JourneyDagEdge.create(journey=journey, left=pipeline, right=pipeline_2)
    journey.component_include_patterns = "*"
    journey.component_exclude_patterns = "P2"
    JourneyService.apply_component_patterns(journey)
    edges = list(JourneyDagEdge.select().where(JourneyDagEdge.journey == journey))
    assert len(edges) == 1
    assert edges[0].right_id == pipeline.id


# --- add_component_to_matching_journeys ---


@pytest.mark.integration
def test_add_component_to_matching_journeys_matches(test_db, journey, project, pipeline):
    journey.component_include_patterns = "*"
    journey.save()
    JourneyService.add_component_to_matching_journeys(pipeline)
    edges = list(JourneyDagEdge.select().where(JourneyDagEdge.journey == journey))
    assert len(edges) == 1
    assert edges[0].left_id is None
    assert edges[0].right_id == pipeline.id


@pytest.mark.integration
def test_add_component_to_matching_journeys_no_include_skips(test_db, journey, pipeline):
    JourneyService.add_component_to_matching_journeys(pipeline)
    assert JourneyDagEdge.select().where(JourneyDagEdge.journey == journey).count() == 0


@pytest.mark.integration
def test_add_component_to_matching_journeys_excluded(test_db, journey, pipeline):
    journey.component_include_patterns = "*"
    journey.component_exclude_patterns = "P1"
    journey.save()
    JourneyService.add_component_to_matching_journeys(pipeline)
    assert JourneyDagEdge.select().where(JourneyDagEdge.journey == journey).count() == 0


@pytest.mark.integration
def test_add_component_to_matching_journeys_only_matching_journey(test_db, journey, journey_2, pipeline):
    journey.component_include_patterns = "P1"
    journey.save()
    journey_2.component_include_patterns = "other-*"
    journey_2.save()
    JourneyService.add_component_to_matching_journeys(pipeline)
    assert JourneyDagEdge.select().where(JourneyDagEdge.journey == journey).count() == 1
    assert JourneyDagEdge.select().where(JourneyDagEdge.journey == journey_2).count() == 0


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
    ret_action = JourneyService.get_action_by_implementation(journey.id, ActionImpl.CALL_WEBHOOK.value)
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
