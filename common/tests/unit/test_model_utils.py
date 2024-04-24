import pytest

from common.model import walk
from common.tests import fake_models


@pytest.mark.unit
def test_walk_models_module():
    """Model walk works when passed a module to walk."""
    model_map = walk(fake_models)
    # Note: Did not paramaterize this using pytest.parametrize because that would invoke `walk` repeatedly.
    for key in ("common.tests.fake_models.model_a.FakeModelA", "common.tests.fake_models.model_b.FakeModelB"):
        assert key in model_map, f"Model map is missing key: {key}"


@pytest.mark.unit
def test_walk_models_default():
    """Not specifying a module to walk defaults to our model schema."""
    model_map = walk()
    # Not an exhaustive list, just spot checking. Also see note in `test_walk_models_module` about pytest.parametrize.
    for key in ("common.entities.company.Company", "common.entities.user.User"):
        assert key in model_map, f"Model map is missing key: {key}"

    # Make sure that models outside the default models module aren't collected by mistake
    unexpected_key = "common.tests.fake_models.model_a.FakeModelA"
    assert unexpected_key not in model_map, f"Model map contained unexpected key: {unexpected_key}"

    # Make sure that BaseEntity and RbacEntity are not present in the keylist
    for omitted_key in ("common.entities.base_entity.RbacEntity", "common.entities.base_entity.BaseEntity"):
        assert omitted_key not in model_map, f"Model map contained unexpected key: {omitted_key}"
