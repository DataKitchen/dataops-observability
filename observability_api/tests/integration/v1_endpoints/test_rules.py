from http import HTTPStatus
from uuid import uuid4

import pytest

from common.entities import Action, AlertLevel, Journey, Pipeline, Rule, RunState
from common.events.v1 import TestStatuses


@pytest.fixture
def error_pattern():
    return {
        "when": "all",
        "conditions": [
            {"task_status": {"matches": "FAILED"}},
        ],
    }


@pytest.fixture
def task_status_warning_pattern():
    return {
        "when": "all",
        "conditions": [
            {"task_status": {"matches": "COMPLETED_WITH_WARNINGS"}},
        ],
    }


@pytest.fixture
def journey1(project):
    return Journey.create(name="J1", description="Test Journey Description 1", project=project)


@pytest.fixture
def journey2(project):
    return Journey.create(name="J2", description="Test Journey Description 2", project=project)


@pytest.fixture
def pipeline1(project, journey1):
    return Pipeline.create(key="Pipeline-1", project=project)


@pytest.fixture
def pipeline2(project, journey2):
    return Pipeline.create(key="Pipeline-2", project=project)


@pytest.fixture
def email_action(company):
    return Action.create(
        name="Test Email Action",
        action_impl="SEND_EMAIL",
        company=company,
        action_args={"from_address": "testuser@domain.com"},
    )


@pytest.fixture
def webhook_action(company):
    return Action.create(
        name="Test Webhook Action",
        action_impl="CALL_WEBHOOK",
        company=company,
    )


@pytest.fixture
def rules(
    journey1,
    journey2,
    pipeline1,
    pipeline2,
    email_action,
    error_pattern,
    task_status_warning_pattern,
    email_action_args,
):
    rules = {journey1: [], journey2: []}
    for pipeline, journey in ((pipeline1, journey1), (pipeline2, journey2)):
        for data in (error_pattern, task_status_warning_pattern):
            rules[journey].append(
                Rule.create(
                    rule_schema="simple_v1",
                    rule_data=data,
                    journey=journey,
                    action=email_action.action_impl,
                    action_args=email_action_args,
                    component=pipeline,
                )
            )
    return rules


@pytest.fixture
def email_action_args():
    return {
        "template": "TemplateName",
        "recipients": ["test1@domain.com", "test2@domain.com"],
    }


@pytest.mark.integration
def test_list_rules_ok(client, g_user, journey1, pipeline1, email_action, email_action_args, rules):
    response = client.get(f"/observability/v1/journeys/{journey1.id}/rules")
    assert response.status_code == HTTPStatus.OK, response.json

    expected_total = len(rules[journey1])
    found_total = response.json["total"]

    assert expected_total == found_total, f"Got {found_total} rules but expected {expected_total}"
    for rule in response.json["entities"]:
        assert rule["component"] == str(pipeline1.id)
        assert rule["rule_schema"] == "simple_v1"
        assert "when" in rule["rule_data"]
        assert rule["action"] == email_action.action_impl
        assert rule["action_args"] == email_action_args


@pytest.mark.integration
def test_list_rules_no_result(client, g_user, project):
    journey = Journey.create(name="1", description="Test Journey Description 2", project=project)
    response = client.get(f"/observability/v1/journeys/{journey.id}/rules")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == 0


@pytest.mark.integration
def test_list_rules_not_found(client, g_user):
    response = client.get(f"/observability/v1/journeys/{uuid4()}/rules")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_admin_user_list_rules_not_found(client, g_user_2_admin):
    response = client.get(f"/observability/v1/journeys/{uuid4()}/rules")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_list_rules_forbidden(client, g_user_2, journey1, pipeline1, email_action, email_action_args, rules):
    response = client.get(f"/observability/v1/journeys/{journey1.id}/rules")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != journey1.project.organization.company.id


@pytest.mark.integration
def test_admin_user_list_rules_ok(client, g_user_2_admin, journey1, pipeline1, email_action, email_action_args, rules):
    response = client.get(f"/observability/v1/journeys/{journey1.id}/rules")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["total"] == len(rules[journey1])
    assert g_user_2_admin.user.primary_company.id != journey1.project.organization.company.id


@pytest.mark.integration
def test_list_rules_with_pagination(client, g_user, journey1, pipeline1, rules):
    expected_total = len(rules[journey1])

    page_result = client.get(f"/observability/v1/journeys/{journey1.id}/rules", query_string={"count": 1, "page": 2})
    assert page_result.status_code == HTTPStatus.OK, page_result.json
    assert page_result.json["total"] == expected_total
    assert len(page_result.json["entities"]) == 1

    page_result = client.get(f"/observability/v1/journeys/{journey1.id}/rules", query_string={"count": 1, "page": 3})
    assert page_result.status_code == HTTPStatus.OK, page_result.json
    assert page_result.json["total"] == expected_total
    assert len(page_result.json["entities"]) == 0


@pytest.mark.integration
@pytest.mark.parametrize("asc", (True, False))
def test_list_rules_sorted(client, g_user, journey1, pipeline1, rules, asc):
    response = client.get(
        f"/observability/v1/journeys/{journey1.id}/rules", query_string={"sort": "ASC" if asc else "DESC"}
    )
    assert response.status_code == HTTPStatus.OK, response.json

    expected_rules = rules[journey1]
    expected_total = len(expected_rules)
    found_total = response.json["total"]
    if not asc:
        expected_rules.reverse()

    assert expected_total == found_total, f"Got {found_total} rules but expected {expected_total}"
    for expected_rule, actual_rule in zip(expected_rules, response.json["entities"]):
        assert str(expected_rule.id) == actual_rule["id"]


@pytest.mark.integration
def test_get_rule_info(client, g_user, pipeline1, rules, email_action, journey1):
    rule = rules[journey1][0]
    response = client.get(f"/observability/v1/rules/{rule.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(rule.id), f"Expected id {rule.id} but got {data.get('id')}"
    assert data["rule_schema"] == rule.rule_schema
    assert data["rule_data"] == rule.rule_data
    assert data["action"] == email_action.action_impl
    assert data["action_args"] == rule.action_args


@pytest.mark.integration
def test_get_rule_not_found(client, g_user):
    response = client.get(f"/observability/v1/rules/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_admin_user_get_rule_not_found(client, g_user_2_admin):
    response = client.get(f"/observability/v1/rules/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_get_rule_info_forbidden(client, g_user_2, pipeline1, rules, email_action, journey1):
    rule = rules[journey1][0]
    response = client.get(f"/observability/v1/rules/{rule.id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != rule.journey.project.organization.company.id


@pytest.mark.integration
def test_admin_user_get_rule_info_ok(client, g_user_2_admin, pipeline1, rules, email_action, journey1):
    rule = rules[journey1][0]
    response = client.get(f"/observability/v1/rules/{rule.id}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert g_user_2_admin.user.primary_company.id != rule.journey.project.organization.company.id


@pytest.mark.integration
def test_post_email_rule_ok(client, g_user, journey1, pipeline1, email_action, email_action_args, error_pattern):
    post_data = {
        "component": pipeline1.id,
        "rule_schema": "simple_v1",
        "rule_data": error_pattern,
        "action": email_action.action_impl,
        "action_args": email_action_args,
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json=post_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    rule = response.json
    assert rule["id"] is not None
    assert rule["action"] == email_action.action_impl
    assert rule["action_args"] == post_data["action_args"]
    assert rule["rule_schema"] == post_data["rule_schema"]
    assert rule["rule_data"] == post_data["rule_data"]
    assert rule["component"] == str(pipeline1.id)


@pytest.mark.integration
def test_post_webhook_rule_ok(client, g_user, journey1, pipeline1, webhook_action, error_pattern):
    webhook_action_args = {
        "url": "http://example.com",
    }
    expected_webhook_action_args = {
        "url": "http://example.com",
        "method": "POST",
        "headers": None,
        "payload": None,
    }
    post_data = {
        "component": pipeline1.id,
        "rule_schema": "simple_v1",
        "rule_data": error_pattern,
        "action": webhook_action.action_impl,
        "action_args": webhook_action_args,
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json=post_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    rule = response.json
    assert rule["id"] is not None
    assert rule["action"] == webhook_action.action_impl
    assert rule["action_args"] == expected_webhook_action_args
    assert rule["rule_schema"] == post_data["rule_schema"]
    assert rule["rule_data"] == post_data["rule_data"]
    assert rule["component"] == str(pipeline1.id)


@pytest.mark.integration
def test_post_webhook_rule_invalid_args(client, g_user, journey1, pipeline1, webhook_action, error_pattern):
    post_data = {
        "rule_schema": "simple_v1",
        "rule_data": error_pattern,
        "action": webhook_action.action_impl,
        "action_args": {},
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json=post_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_post_email_rule_invalid_rule_data(client, g_user, journey1, pipeline1, email_action, email_action_args):
    post_data = {
        "rule_schema": "simple_v1",
        "rule_data": "string, not dict",
        "action": email_action.id,
        "action_args": email_action_args,
    }
    email_invalid_data = post_data.copy()
    email_invalid_data["action_args"]["subject"] = ""

    def _test_bad_response(post):
        response = client.post(
            f"/observability/v1/journeys/{journey1.id}/rules",
            headers={"Content-Type": "application/json"},
            json=post,
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, response.json

    for data in [post_data, email_invalid_data]:
        _test_bad_response(data)


@pytest.mark.integration
def test_post_email_rule_invalid_pattern_2(client, g_user, journey1, pipeline1, email_action, email_action_args):
    bad_pattern = {
        "when": "all",
        "conditions": [
            {"status": "FAILED"},
        ],
    }
    post_data = {
        "rule_schema": "simple_v1",
        "rule_data": bad_pattern,
        "action": email_action.action_impl,
        "action_args": email_action_args,
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json=post_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_post_email_rule_default_value(
    client, g_user, journey1, pipeline1, email_action, email_action_args, error_pattern
):
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": error_pattern,
            "action": email_action.action_impl,
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert response.json["action_args"] == email_action_args


@pytest.mark.integration
def test_post_email_rule_default_value(
    client, g_user, journey1, pipeline1, email_action, email_action_args, error_pattern
):
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": error_pattern,
            "action": email_action.action_impl,
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert response.json["action_args"] == email_action_args


@pytest.mark.integration
@pytest.mark.parametrize(
    "condition",
    [
        {"run_state": {"matches": RunState.COMPLETED.name, "count": 3}},
        {"test_status": {"matches": TestStatuses.PASSED.name}},
        {"instance_alert": {"level_matches": [AlertLevel.WARNING.name]}},
    ],
)
def test_post_rule_valid_conditions(condition, client, g_user, journey1, pipeline1, email_action, email_action_args):
    rule_data = {
        "when": "all",
        "conditions": [
            condition,
        ],
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": rule_data,
            "action": email_action.action_impl,
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    assert response.json["action_args"] == email_action_args


@pytest.mark.integration
def test_post_rule_with_invalid_test_status_pattern(
    client, g_user, journey1, pipeline1, email_action, email_action_args
):
    rule_data = {
        "when": "all",
        "conditions": [
            {"test_status": {"matches": "COMPLETED"}},
        ],
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": rule_data,
            "action": email_action.action_impl,
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_post_email_rule_journey_not_found(client, g_user, email_action, email_action_args, error_pattern):
    response = client.post(
        f"/observability/v1/journeys/{uuid4()}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": error_pattern,
            "action": email_action.action_impl,
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_email_rule_component_not_found(client, g_user, journey1, email_action, email_action_args, error_pattern):
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": error_pattern,
            "action": email_action.action_impl,
            "action_args": email_action_args,
            "component": f"{uuid4()}",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_post_email_rule_action_not_found(client, g_user, journey1, pipeline1, email_action_args):
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "test schema v1",
            "rule_data": {},
            "action": "some unknown action",
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_post_email_rule_duplicate_action_impl(
    client, g_user, journey1, pipeline1, company, email_action, email_action_args
):
    Action.create(name="Test Action2", action_impl=email_action.action_impl, company=company)
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "test schema v1",
            "rule_data": {"when": "any", "conditions": [{"task_status": {"matches": "FAILED"}}]},
            "action": email_action.action_impl,
            "action_args": email_action_args,
        },
    )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR, response.json


@pytest.mark.integration
def test_post_email_rule_missing_action(client, g_user, journey1, pipeline1, error_pattern):
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={
            "rule_schema": "simple_v1",
            "rule_data": error_pattern,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_post_email_rule_with_origin_header(
    client, g_user, journey1, pipeline1, email_action, email_action_args, error_pattern
):
    post_data = {
        "rule_schema": "simple_v1",
        "rule_data": error_pattern,
        "action": email_action.action_impl,
        "action_args": email_action_args,
    }
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json=post_data,
    )
    assert response.status_code == HTTPStatus.CREATED, response.json
    rule = response.json
    assert rule["id"] is not None
    assert rule["action"] == email_action.action_impl
    assert rule["action_args"] == {**post_data["action_args"]}
    assert rule["rule_schema"] == post_data["rule_schema"]
    assert rule["rule_data"] == post_data["rule_data"]
    assert rule["component"] is None


@pytest.mark.integration
def test_post_rule_forbidden(client, g_user_2, journey1):
    response = client.post(
        f"/observability/v1/journeys/{journey1.id}/rules",
        headers={"Content-Type": "application/json"},
        json={},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != journey1.project.organization.company.id


@pytest.mark.integration
def test_delete_rule_project(client, g_user, journey1, pipeline1, rules):
    rule = rules[journey1][0]
    response = client.delete(f"/observability/v1/rules/{rule.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert not response.data
    assert len(Rule.select().where(Rule.id == rule.id)) == 0


@pytest.mark.integration
def test_admin_user_delete_rule_ok(client, g_user_2_admin, journey1, rules):
    rule = rules[journey1][0]
    response = client.delete(f"/observability/v1/rules/{rule.id}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert g_user_2_admin.user.primary_company.id != rule.journey.project.organization.company.id


@pytest.mark.integration
def test_rule_delete_not_found(client, g_user):
    # Pre-check
    assert Rule.select().count() == 0

    response = client.delete(f"/observability/v1/rules/{uuid4()}")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json
    assert not response.data
    assert Rule.select().count() == 0


@pytest.mark.integration
def test_delete_rule_forbidden(client, g_user_2, journey1, rules):
    response = client.delete(f"/observability/v1/rules/{rules[journey1][0].id}")
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != journey1.project.organization.company.id


@pytest.mark.integration
def test_patch_webhook_rule_ok(client, g_user, journey1, pipeline1, rules, webhook_action):
    rule = rules[journey1][0]
    new_data = {
        "rule_data": {"when": "any", "conditions": [{"task_status": {"matches": "FAILED"}}]},
        "action": webhook_action.action_impl,
        "action_args": {
            "url": "http://example.com",
        },
    }
    expected_webhook_action_args = {
        "url": "http://example.com",
        "method": "POST",
        "headers": None,
        "payload": None,
    }
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(rule.id)
    assert data["rule_data"] == new_data["rule_data"]
    assert data["action"] == webhook_action.action_impl
    assert data["action_args"] == expected_webhook_action_args
    # TODO: Since we're using a singular action at the moment, this doesn't make as a test. If we allow the creation
    #       of custom action_impl, this will make sense.
    #       assert Rule.get_by_id(rule.id).action.id == new_action.id


@pytest.mark.integration
def test_patch_webhook_rule_invalid_args(client, g_user, journey1, rules, webhook_action):
    rule = rules[journey1][0]
    new_data = {
        "rule_data": {"when": "any", "conditions": [{"task_status": {"matches": "FAILED"}}]},
        "action": webhook_action.action_impl,
        "action_args": {},
    }
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_email_rule_invalid_action(client, g_user, journey1, pipeline1, rules):
    rule = rules[journey1][0]
    new_data = {"action": "other"}
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_email_rule_not_found(client, g_user):
    new_data = {"rule_data": {"when": "any", "conditions": [{"task_status": {"matches": "FAILED"}}]}}
    response = client.patch(
        f"/observability/v1/rules/{uuid4()}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_patch_email_rule_component_not_found(client, g_user, journey1, pipeline1, rules):
    rule = rules[journey1][0]
    new_data = {"component": str(uuid4())}
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.integration
def test_patch_email_rule_component_to_null(client, g_user, journey1, pipeline1, rules):
    rule = rules[journey1][0]
    new_data = {"component": None}
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.OK, response.json


@pytest.mark.integration
def test_patch_email_rule_invalid_body(client, g_user, journey1, pipeline1, rules):
    rule = rules[journey1][0]
    new_data = {"invalid field": "data"}
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json


@pytest.mark.integration
def test_patch_email_rule_duplicate_action_impl(
    client, g_user, journey1, pipeline1, rules, email_action, company, email_action_args
):
    Action.create(name="Test Action2", action_impl=email_action.action_impl, company=company)
    rule = rules[journey1][0]
    new_data = {"action": email_action.action_impl, "action_args": email_action_args}
    response = client.patch(
        f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json=new_data
    )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR, response.json


@pytest.mark.integration
def test_patch_email_rule_with_origin_header(client, g_user, journey1, rules, email_action, email_action_args):
    rule = rules[journey1][0]
    new_data = {
        "rule_data": {"when": "any", "conditions": [{"task_status": {"matches": "COMPLETED"}}]},
        "action": email_action.action_impl,
        "action_args": email_action_args,
    }
    response = client.patch(
        f"/observability/v1/rules/{rule.id}",
        headers={"Content-Type": "application/json"},
        json=new_data,
    )
    assert response.status_code == HTTPStatus.OK, response.json
    data = response.json
    assert data["id"] == str(rule.id)
    assert data["rule_data"] == new_data["rule_data"]
    assert data["action"] == email_action.action_impl
    assert data["action_args"] == {**new_data["action_args"]}


@pytest.mark.integration
def test_patch_rule_forbidden(client, g_user_2, journey1, rules):
    rule = rules[journey1][0]
    response = client.patch(f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json={})
    assert response.status_code == HTTPStatus.FORBIDDEN, response.json
    assert g_user_2.primary_company.id != rule.journey.project.organization.company.id


@pytest.mark.integration
def test_admin_user_patch_webhook_rule_ok(client, g_user_2_admin, journey1, pipeline1, rules, webhook_action):
    rule = rules[journey1][0]
    response = client.patch(f"/observability/v1/rules/{rule.id}", headers={"Content-Type": "application/json"}, json={})
    assert response.status_code == HTTPStatus.OK, response.json
    assert g_user_2_admin.user.primary_company.id != rule.journey.project.organization.company.id
