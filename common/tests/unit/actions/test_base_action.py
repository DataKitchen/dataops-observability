from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from common.actions.action import BaseAction, ActionTemplateRequired, ActionResult


@pytest.fixture
def sub_class():
    return type("BaseActionSubclass", (BaseAction,), {})


@pytest.fixture
def sub_class_tpl():
    return type("BaseActionSubclassTemplate", (BaseAction,), {"requires_action_template": True})


@pytest.mark.unit
def test_base_action_template_validation(sub_class, sub_class_tpl, action):
    # Instance should be created
    sub_class(action, {})
    sub_class(None, {})
    sub_class_tpl(action, {})

    # Instance creation should fail
    with pytest.raises(ActionTemplateRequired):
        sub_class_tpl(None, {})


@pytest.mark.unit
def test_base_action_argument_merging(sub_class, action):
    action.action_args = {"arg1": "val1", "arg2": "val2"}
    override_args = {"arg3": "val3", "arg2": "valX"}
    action_inst = sub_class(action, override_args)
    expected_args = {"arg1": "val1", "arg2": "valX", "arg3": "val3"}
    assert action_inst.arguments == expected_args


@pytest.mark.unit
def test_base_action_template_arguments(sub_class, action):
    action.action_args = {"arg1": "val1", "arg2": "val2"}
    action_inst = sub_class(action, {})
    assert action_inst.arguments == action.action_args


@pytest.mark.unit
def test_base_action_override_arguments(sub_class):
    override_args = {"arg1": "val1", "arg2": "val2"}
    action_inst = sub_class(None, override_args)
    assert action_inst.arguments == override_args


@pytest.mark.unit
def test_base_action_arg_validation_empty(sub_class):
    action_inst = sub_class(None, {})
    assert action_inst.arguments == {}


@pytest.mark.unit
def test_base_action_arg_validation_ok(sub_class):
    with patch.object(sub_class, "required_arguments", {"some_arg", "another_arg"}):
        sub_class(None, {"some_arg": 1, "another_arg": None})


@pytest.mark.unit
def test_base_action_arg_validation_fail(sub_class):
    with patch.object(sub_class, "required_arguments", {"some_arg", "another_arg"}):
        with pytest.raises(ValueError):
            sub_class(None, {"some_wrong_arg": 1, "another_arg": None})


@pytest.mark.unit
def test_base_action_execute():
    uuid = uuid4()
    result = ActionResult(True, {"worked": "yes"}, None)
    run_mock = Mock(return_value=result)
    rule_mock = Mock()
    store_mock = Mock()
    event_mock = object()
    sub_class = type("BaseActionRun", (BaseAction,), {"_run": run_mock, "_store_action_result": store_mock})
    action_inst = sub_class(None, {})
    ret = action_inst.execute(event_mock, rule_mock, uuid)
    assert ret == result.result
    run_mock.assert_called_with(event_mock, rule_mock, uuid)
    store_mock.assert_called_once_with(result)
