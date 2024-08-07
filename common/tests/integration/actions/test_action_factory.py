import pytest

from common.actions.action_factory import ACTION_CLASS_MAP
from common.schemas.action_schemas import ValidActions


@pytest.mark.integration
def test_check_all_action_implemented():
    # Check that valid actions are represented in the action factory map and vice versa.
    assert ACTION_CLASS_MAP.keys() == set(a.name for a in ValidActions)
