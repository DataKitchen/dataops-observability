import pytest

from common.schemas.action_schemas import ValidActions
from rules_engine.actions import ACTION_CLASS_MAP


@pytest.mark.integration
def test_check_all_action_implemented():
    # Check that valid actions are represented in the action factory map and vice versa.
    assert ACTION_CLASS_MAP.keys() == set(a.name for a in ValidActions)
