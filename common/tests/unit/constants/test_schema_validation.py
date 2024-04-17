import re

import pytest

from common.constants import EXTENDED_ALPHANUMERIC_REGEX


@pytest.mark.unit
@pytest.mark.parametrize("value", ("", " ", "z", "åêà", "aA1", "b B", " c ", "d_D", "123_abc 456 EDF"))
def test_extended_alphanumeric_regex_matching(value):
    assert re.match(EXTENDED_ALPHANUMERIC_REGEX, value)


@pytest.mark.unit
@pytest.mark.parametrize("value", ("!", "_", "_a", "b_c-d"))
def test_extended_alphanumeric_regex_not_matching(value):
    assert not re.match(EXTENDED_ALPHANUMERIC_REGEX, value)
