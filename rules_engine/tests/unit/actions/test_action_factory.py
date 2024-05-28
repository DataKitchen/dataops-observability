from enum import Enum
from unittest.mock import Mock, patch

import pytest

from common.entities import Action, Rule
from rules_engine.actions import ACTION_CLASS_MAP, ImplementationNotFound, InvalidActionTemplate, action_factory


class TestActionImpl(Enum):
    DO_SOMETHING = "DO_SOMETHING"
    DO_ANOTHER_THING = "DO_ANOTHER_THING"


@pytest.fixture
def rule():
    return Rule(pipeline_id="PIPELINE_ID", action="DO_SOMETHING", action_args={"arg1": "val1"})


@pytest.fixture
def action():
    return Action(action_impl=TestActionImpl.DO_SOMETHING, action_args={"arg2": "val2"})


@pytest.fixture
def action_class_mock():
    class_mock = Mock()
    with patch.dict(ACTION_CLASS_MAP, clear=True, DO_SOMETHING=class_mock):
        yield class_mock


@pytest.mark.unit
@pytest.mark.parametrize("use_template", (True, False), ids=("using_template", "without_template"))
def test_create_action_ok(use_template, rule, action_class_mock, action):
    # Setup
    action_object_mock = object()
    action_class_mock.return_value = action_object_mock
    template = action if use_template else None

    # Run
    action_object = action_factory(rule, template)

    # Verify
    action_class_mock.assert_called_once_with(template, rule.action_args)
    assert action_object is action_object_mock


@pytest.mark.unit
def test_create_action_unknown_impl(rule, action_class_mock):
    rule.action = "DO_ANOTHER_THING"
    with pytest.raises(ImplementationNotFound, match="is not recognized"):
        action_factory(rule, None)


@pytest.mark.unit
def test_create_action_bad_template(rule, action_class_mock, action):
    # Setup
    action.action_impl = TestActionImpl.DO_ANOTHER_THING
    with pytest.raises(InvalidActionTemplate, match="doesn't match Rule action"):
        action_factory(rule, action)
