import random
import sys
from collections.abc import MutableMapping
from copy import copy
from datetime import datetime, timezone
from unicodedata import category

import pytest

from common.predicate_engine._operators import OPERAND_MAP, split_operators
from common.predicate_engine.query import ALL, ANY, ATLEAST, EXACT_N, R, get_rule_fields, getattr_recursive

from .assertions import assertRuleEqual, assertRuleMatches, assertRuleNotMatches

ALL_UNICODE = "".join(chr(i) for i in range(sys.maxunicode))
"""All valid unicode chars on this system."""

UNICODE_LETTERS = "".join(c for c in ALL_UNICODE if (category(c) in ("Lu", "Ll", "Nl") and c != "/"))
"""String of unicode characters limited to Upper and Lowercase letters, and numbers."""


def unicode_word():
    """Return a very nasty unicode string word."""
    return "".join(random.choice(UNICODE_LETTERS) for i in range(8))


def unique_text_array(count=15):
    """Return up to `n` unique strings where each `word` is an item in a list."""
    return [unicode_word() for x in range(random.randrange(1, count))]


class ReallyDumbDict(MutableMapping):
    """A dumb dict for testing fallback values in exotic scenarios."""

    BANNED_GETITEM = ("foo", "bar")
    BANNED_GET = ("baz", "fizz")

    def __init__(self, *args, **kwds):
        self.store = {}
        self.update(*args, **kwds)

    def __getitem__(self, key):
        if key in ReallyDumbDict.BANNED_GETITEM:
            raise KeyError("How did we get here?")
        return self.store[key]

    def get(self, key, default=None):
        if key in ReallyDumbDict.BANNED_GET:
            raise AttributeError("Why would you look for THAT?")
        return super().get(key, default=default)

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __len__(self):
        return len(self.store)

    def __iter__(self):
        return iter(self.store)

    def __contains__(self, value):
        return value in self.store


class SimpleObj:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class FakeObject:
    """Test class for object matching tests"""

    def __init__(self, a: object, b: object, total_things=4, val_array=None) -> None:
        self.a = a
        self.b = b
        self.total_things = total_things
        self.str_value = "fleem"
        self.int_value = 42  # It's always gonna be 42 man
        self.null_value = None
        self.dict_value = {"test": 1}
        self.val_array = val_array or ("boo", "bar", "baz")

    def __str__(self) -> str:
        return f"{self.a} - {self.b}"

    @property
    def averages(self) -> int:
        return 3


@pytest.fixture(scope="session")
def simple_entity_dict():
    yield {"a": 3, "b": "test"}


@pytest.mark.parametrize(
    "input,expected",
    (
        # Values with a valid operator should yield that operator
        ("test__exact", ("test", "exact")),
        ("test__iexact", ("test", "iexact")),
        ("test__contains", ("test", "contains")),
        ("test__icontains", ("test", "icontains")),
        ("test__in", ("test", "in")),
        ("test__gt", ("test", "gt")),
        ("test__gte", ("test", "gte")),
        ("test__lt", ("test", "lt")),
        ("test__lte", ("test", "lte")),
        ("test__startswith", ("test", "startswith")),
        ("test__istartswith", ("test", "istartswith")),
        ("test__endswith", ("test", "endswith")),
        ("test__iendswith", ("test", "iendswith")),
        ("test__range", ("test", "range")),
        ("test__isnull", ("test", "isnull")),
        ("test__regex", ("test", "regex")),
        ("test__iregex", ("test", "iregex")),
        # Values with a default operator that span attributes should yield that attrname and operator
        ("test__fizz__exact", ("test__fizz", "exact")),
        ("test__fizz__iexact", ("test__fizz", "iexact")),
        ("test__fizz__contains", ("test__fizz", "contains")),
        ("test__fizz__icontains", ("test__fizz", "icontains")),
        ("test__fizz__in", ("test__fizz", "in")),
        ("test__fizz__gt", ("test__fizz", "gt")),
        ("test__fizz__gte", ("test__fizz", "gte")),
        ("test__fizz__lt", ("test__fizz", "lt")),
        ("test__fizz__lte", ("test__fizz", "lte")),
        ("test__fizz__startswith", ("test__fizz", "startswith")),
        ("test__fizz__istartswith", ("test__fizz", "istartswith")),
        ("test__fizz__endswith", ("test__fizz", "endswith")),
        ("test__fizz__iendswith", ("test__fizz", "iendswith")),
        ("test__fizz__range", ("test__fizz", "range")),
        ("test__fizz__isnull", ("test__fizz", "isnull")),
        ("test__fizz__regex", ("test__fizz", "regex")),
        ("test__fizz__iregex", ("test__fizz", "iregex")),
    ),
)
@pytest.mark.unit
def test_split_operators(input, expected):
    """Query operators can be split off."""
    actual = split_operators(input)
    assert expected == actual


@pytest.mark.parametrize(
    "input",
    (
        "__exact",  # Missing attribute name
        "foo__eexact",  # misspelled operator
        "nope",  # Missing operator
    ),
)
@pytest.mark.unit
def test_split_operator_bad(input):
    with pytest.raises(ValueError):
        split_operators(input)


@pytest.mark.parametrize(
    "rule", (R(a__lte=5), R(a__lte=4) & R(b__contains="e"), R(a__lte=4) | R(b__contains="e"), ~R(a__exact=4))
)
@pytest.mark.unit
def test_matching_rules_true(rule, simple_entity, simple_entity_dict):
    """Rules that should match successfully."""
    assertRuleMatches(rule, simple_entity)
    assertRuleMatches(rule, simple_entity_dict)


@pytest.mark.parametrize("rule", (R(a__gt=7), R(a__lte=4) & R(b__contains="z"), ~R(a__exact=3)))
@pytest.mark.unit
def test_matching_rules_false(rule, simple_entity, simple_entity_dict):
    """Rules that should fail to match."""
    assertRuleNotMatches(rule, simple_entity)
    assertRuleNotMatches(rule, simple_entity_dict)


@pytest.mark.parametrize(
    "rule",
    (
        R(a__gt=None),
        R(null__contains=3) | R(null__endswith="None") | R(null__exact="None"),
    ),
)
@pytest.mark.unit
def test_matching_invalid_data_types(rule, simple_entity):
    """Rules with mismatched datatypes that cannot be compared fail evaluations."""
    assertRuleNotMatches(rule, simple_entity)


@pytest.mark.parametrize(
    "rule",
    (
        R(timestamp__gte=datetime.now(timezone.utc)),
        R(timestamp_dt__gte=datetime.now()),
    ),
)
@pytest.mark.unit
def test_compare_naive_tzaware_datetimes(rule, simple_entity):
    """Comparing tzaware datetimes with non-tzaware datetimes is a failed match rather than an Exception."""
    assertRuleNotMatches(rule, simple_entity)


@pytest.mark.unit
def test_exact(simple_entity):
    """Exact operator functions as expected."""
    rule_obj = R(str_value__exact="fleem") & R(int_value__exact=42)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_iexact(simple_entity):
    """Case insensitive operations function as expected."""
    rule_obj = R(str_value__iexact="FleeM") & R(int_value__exact=42)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_contains_true(simple_entity):
    """Contains operator yields True for matching values."""
    rule_obj = R(str_value__contains="ee")
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_contains_false(simple_entity):
    """Contains operator yields True for matching values."""
    rule_obj = R(str_value__contains="foo") & R(int_value__exact=42)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_icontains_true(simple_entity):
    """Case insensitive contains operator Yields True for matching values."""
    rule_obj = R(str_value__icontains="EE") & R(int_value__exact=42)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_icontains_false(simple_entity):
    """Case insensitive contains operator Yields False for non-matching values."""
    rule_obj = R(str_value__icontains="BILBO") & R(int_value__exact=42)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_in_true(simple_entity):
    """In operator yields True for matching values."""
    rule_obj = R(str_value__in=("spoo", "hpqa", "fleem")) & R(int_value__in=(42, 43, 44))
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_in_false(simple_entity):
    """In operator yields False for non-matching values."""
    rule_obj = R(str_value__in=("spoo", "hpqa", "fleemo")) | R(int_value__in=(43, 44))
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_lt_true(simple_entity):
    """Less-than operator yields True for matching values."""
    rule_obj = R(str_value__exact="fleem") & R(int_value__lt=43)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_lt_false(simple_entity):
    """Less-than operator yields False for non-matching values."""
    rule_obj = R(str_value__exact="fleem") & R(int_value__lt=42)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_gt_true(simple_entity):
    """Greater-than operator yields True for matching values."""
    rule_obj = R(str_value__exact="fleem") & R(int_value__gt=41)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_gt_false(simple_entity):
    """Greater-than operator yields False for non-matching values."""
    rule_obj = R(str_value__exact="fleem") & R(int_value__gt=44)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_lte_true(simple_entity):
    """Less-than-equal operator yields True for matching values."""
    rule_obj_1 = R(str_value__exact="fleem") & R(int_value__lte=42)
    assertRuleMatches(rule_obj_1, simple_entity)

    rule_obj_2 = R(str_value__exact="fleem") & R(int_value__lte=43)
    assertRuleMatches(rule_obj_2, simple_entity)


@pytest.mark.unit
def test_gte_true(simple_entity):
    """Greater-than-equal operator yeilds True for matching values."""
    rule_obj_1 = R(str_value__exact="fleem") & R(int_value__gte=42)
    assertRuleMatches(rule_obj_1, simple_entity)

    rule_obj_2 = R(str_value__exact="fleem") & R(int_value__gte=41)
    assertRuleMatches(rule_obj_2, simple_entity)


@pytest.mark.unit
def test_startswith_true(simple_entity):
    """Case sensitive startswith operator yields True for matching values."""
    rule_obj = R(str_value__startswith="f")
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_startswith_false(simple_entity):
    """Startswith operator yields False for non-matching values."""
    rule_obj = R(str_value__startswith="F")
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_istartswith_true(simple_entity):
    """Case insensitive istartswith operator yields True for matching values."""
    rule_obj = R(str_value__istartswith="F") & R(int_value__exact=42)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_istartswith_false(simple_entity):
    """Case insensitive istartswith operator yields False for non-matching values."""
    rule_obj = R(str_value__istartswith="S") & R(int_value__exact=42)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_endswith_true(simple_entity):
    """Endswith operator yields True for matching values."""
    rule_obj = R(str_value__endswith="em") & R(int_value__exact=42)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_endswith_false(simple_entity):
    """Endswith operator yields False for non-matching values."""
    rule_obj = R(str_value__endswith="baggins") & R(int_value__exact=42)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_iendswith_true(simple_entity):
    """Case insensitive iendswith operator yields True for matching values."""
    rule_obj = R(str_value__iendswith="eM") & R(int_value__exact=42)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_iendswith_false(simple_entity):
    """Case insensitive iendswith operator yields False for non-matching values."""
    rule_obj = R(str_value__iendswith="spaghetti") & R(int_value__exact=42)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_range_true(simple_entity):
    """Range operator yields True for matching values."""
    rule_obj = R(int_value__range=(10, 50))
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_range_false(simple_entity):
    """Range operator yields False for non-matching values."""
    rule_obj = R(int_value__range=(60, 90))
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_isnull_true(simple_entity):
    """Isnull operator yields True for matching values."""
    rule_obj = R(null_value__isnull=True) & R(int_value__isnull=False)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_isnull_missing_attr_true(simple_entity):
    """Isnull operator yields True for missing attributes."""
    rule_obj = R(invalid_attribute_name__isnull=True) & R(int_value__isnull=False)
    assertRuleMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_isnull_false(simple_entity):
    """Isnull operator yields False for non-matching values."""
    rule_obj = R(null_value__isnull=False)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_regex_true(simple_entity):
    """Regex operator yields True for matching values."""
    rule_obj_1 = R(str_value__regex="f[a-z]{4}")
    assertRuleMatches(rule_obj_1, simple_entity)

    rule_obj_2 = R(str_value__regex="eem$")
    assertRuleMatches(rule_obj_2, simple_entity)


@pytest.mark.unit
def test_regex_false(simple_entity):
    """Regex operator yields False for non-matching values."""
    rule_obj = R(str_value__regex="^foo[a-z]{4}")
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_iregex_true(simple_entity):
    """Case insensitive iregex operator yields True for matching values."""
    rule_obj_1 = R(str_value__iregex="[A-Z]{5}")
    assertRuleMatches(rule_obj_1, simple_entity)

    rule_obj_2 = R(str_value__iregex="[a-z]{5}")
    assertRuleMatches(rule_obj_2, simple_entity)

    rule_obj_3 = R(str_value__iregex="EEM$")
    assertRuleMatches(rule_obj_3, simple_entity)


@pytest.mark.unit
def test_iregex_false(simple_entity):
    """Case insensitive iregex operator yields True for matching values."""
    rule_obj = R(str_value__iregex="^foo[a-z]{4}")
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_or_true(simple_entity):
    """OR'ing together rules yields True for matching values."""
    rule_obj_1 = R(str_value__isnull=True) | R(int_value__exact=42)
    assertRuleMatches(rule_obj_1, simple_entity)

    # None of these matche, but when OR'd together with rule_obj_1 the resulting object should still
    # yield a postiive match
    bad_rule_1 = R(int_value__exact=43)
    assertRuleNotMatches(bad_rule_1, simple_entity)

    bad_rule_2 = R(null_value__isnull=False)
    assertRuleNotMatches(bad_rule_2, simple_entity)

    rule_obj_2 = rule_obj_1 | bad_rule_1 | bad_rule_2
    assertRuleMatches(rule_obj_2, simple_entity)


@pytest.mark.unit
def test_or_false(simple_entity):
    """OR'ing together rules yields False for non-matching values."""
    rule_obj = R(str_value__isnull=True) | R(int_value__exact=43)
    assertRuleNotMatches(rule_obj, simple_entity)


@pytest.mark.unit
def test_copy():
    """Copying a Rule object should yield new instance values."""
    rule_obj = R(foo__exact="BAR")
    rule_obj_copy = copy(rule_obj)

    assert rule_obj is not rule_obj_copy
    assert rule_obj.children is not rule_obj_copy.children


@pytest.mark.unit
def test_contains():
    """Child instances match in operator."""
    base = R(foo__exact="BAR")
    child = R(foo__exact="BUZZ")
    base.children.append(child)
    assert child in base


@pytest.mark.unit
def test_not_contains():
    """The in operator is falsey when child is not in the rule children."""
    base = R(foo__exact="BAR")
    child = R(foo__exact="BUZZ")
    assert child not in base


@pytest.mark.unit
def test_or_negated(simple_entity):
    """Negating an OR'd together match yields the opposite result."""
    # Start with a rule that should fail to match
    bad_rule = R(str_value__isnull=True) | R(int_value__exact=43)
    assertRuleNotMatches(bad_rule, simple_entity)

    # Negate the rule; the result should now be a successful match
    good_rule = ~bad_rule
    assertRuleMatches(good_rule, simple_entity)


@pytest.mark.unit
def test_recursive_attribute_lookup(simple_entity, nested_entity):
    """Attribute spanning can be followed up the chain."""
    expected = 3
    actual_1 = getattr_recursive(simple_entity, "a")
    assert expected == actual_1

    actual_2 = getattr_recursive(nested_entity, "a__a__a")
    assert expected == actual_2


@pytest.mark.unit
def test_recursive_attribute_lookup_dict_default_val():
    """Fallback value used when hitting an exception in a .get lookup on a mapping object."""
    dumb_dict = ReallyDumbDict(foo=1, bar=1, baz=1, fizz=1)
    expected = "default"
    actual = getattr_recursive(dumb_dict, "foo", "default")
    assert expected == actual


@pytest.mark.unit
def test_recursive_attribute_lookup_dict_fallback():
    """Fallback to attribute lookup used when hitting an exception in a __getitem__ lookup on a mapping object."""
    dumb_dict = ReallyDumbDict(foo=1, bar=1, baz=1, fizz=1)
    dumb_dict.foo = "fallback"
    expected = "fallback"
    actual = getattr_recursive(dumb_dict, "foo")
    assert expected == actual


@pytest.mark.unit
def test_recursive_attribute_lookup_dict_get_exception_attr_fallback():
    """Fallback to attribute lookup used when hitting an exception in a .get lookup on a mapping object."""
    dumb_dict = ReallyDumbDict(foo=1, bar=1, baz=1, fizz=1)
    dumb_dict.baz = "fallback"
    expected = "fallback"
    actual = getattr_recursive(dumb_dict, "baz")
    assert expected == actual


@pytest.mark.unit
def test_recursive_attribute_lookup_dict_get_exception_default_val():
    dumb_dict = ReallyDumbDict(foo=1, bar=1, baz=1, fizz=1)
    expected = "fallback"
    actual = getattr_recursive(dumb_dict, "baz", "fallback")
    assert expected == actual


@pytest.mark.unit
def test_recursive_attribute_lookup_dict_get_exception_attribute_error():
    """AttributeError raised when an exception happens in .get call with no fallback values."""
    dumb_dict = ReallyDumbDict(foo=1, bar=1, baz=1, fizz=1)
    with pytest.raises(AttributeError):
        getattr_recursive(dumb_dict, "baz")


@pytest.mark.unit
def test_recursive_attribute_lookup_dict_getitem_exception_attribute_error():
    """AttributeError raised when an exception happens in __getitem__ call with no fallback values."""
    dumb_dict = ReallyDumbDict(foo=1, bar=1, baz=1, fizz=1)
    with pytest.raises(AttributeError):
        getattr_recursive(dumb_dict, "foo")


@pytest.mark.unit
def test_recursive_attribute_lookup_failure(simple_entity):
    """Recursive attribute lookup handles fallback values."""
    expected = None
    actual = getattr_recursive(simple_entity, "a__b__c", None)
    assert expected == actual


@pytest.mark.unit
def test_get_rulefields():
    """R objects can be inspected for all used fields."""
    search_obj = (
        R(id__isnull=False)
        & R(status__exact="awesome")
        & (R(service_name__exact="Slack") | R(service_name__isnull=True) | R(service_name__iendswith="datakitchen"))
        & ~R(pipeline_tag__in=("this", "that", "the other"))
    )
    expected = {"id", "status", "service_name", "pipeline_tag"}
    actual = get_rule_fields(search_obj)
    assert expected == actual


@pytest.mark.unit
def test_non_rule_OR():
    """Rule objects cannot be OR'd with other types of objects."""
    with pytest.raises(TypeError):
        R(id__isnull=False) | object()


@pytest.mark.unit
def test_non_rule_AND():
    """Rule objects cannot be AND'd with other types of objects."""
    with pytest.raises(TypeError):
        R(id__isnull=False) & object()


@pytest.mark.unit
def test_stringify_rule():
    """Rule objects can be converted to a flat string."""
    search_obj = (
        R(id__isnull=False)
        & (R(service_name__exact="Slack") | R(service_name__iendswith="datakitchen"))
        & ~R(pipeline_tag__in=("this", "that"))
    )
    expected = "(AND: ('id__isnull', False), (OR: ('service_name__exact', 'Slack'), ('service_name__iendswith', 'datakitchen')), (NOT (AND: ('pipeline_tag__in', ('this', 'that')))))"
    actual = str(search_obj)
    assert expected == actual


@pytest.mark.parametrize(
    "rule,expected",
    (
        (R(), False),
        (R(a__exact="b"), True),
        (R() & R(), False),
        (R() | R(), False),
    ),
)
@pytest.mark.unit
def test_rule_boolean(rule, expected):
    """Rules with no children are falsey, rule with children are truthy."""
    actual = bool(rule)
    assert expected == actual


@pytest.mark.parametrize(
    "actual",
    (
        R() | R(),
        R() | R() | R(),
        R() & R(),
        R() & R() & R(),
        R() & R() | R(),
        R() & R() | (R() & R()) & (R() | R()),
    ),
)
@pytest.mark.unit
def test_rule_empty(actual):
    """Combining a bunch of empty rules simply yields a single empty rule."""
    expected = R()
    assertRuleEqual(expected, actual)


@pytest.mark.parametrize("op", ("gt", "gte", "exact", "lt", "lte"))
@pytest.mark.unit
def test_match_all_on_integer_values(op):
    """Test ALL behavior on a large range of random integer values."""
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = [random.randint(-5000, 5000) for _ in range(20)]
        check_value = random.choice(values)
        r_obj = R(**{f"val_array__{op}": ALL(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)
        expected = all([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        assert expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize("op", ("gt", "gte", "exact", "lt", "lte"))
@pytest.mark.unit
def test_match_any_on_integer_values(op):
    """Test ANY behavior on a large range of random integer values."""
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = [random.randint(-5000, 5000) for _ in range(20)]
        check_value = random.choice(values)
        r_obj = R(**{f"val_array__{op}": ANY(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)
        expected = any([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize("op", ("gt", "gte", "exact", "lt", "lte"))
@pytest.mark.unit
def test_match_all_on_float_values(op):
    """Test ALL behavior on a large range of random float values."""
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = [random.uniform(-1000.0, 1000.0) for _ in range(20)]
        check_value = random.choice(values)
        r_obj = R(**{f"val_array__{op}": ALL(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)
        expected = all([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize("op", ("gt", "gte", "exact", "lt", "lte"))
@pytest.mark.unit
def test_match_any_on_float_values(op):
    """Test ANY behavior on a large range of random float values."""
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = [random.uniform(-1000.0, 1000.0) for _ in range(20)]
        check_value = random.choice(values)
        r_obj = R(**{f"val_array__{op}": ANY(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)
        expected = any([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize("op", ("gt", "gte", "exact", "lt", "lte"))
@pytest.mark.unit
def test_match_all_on_datetime_values(op):
    """Test ALL behavior on a large range of random datetime values."""
    max_int = datetime.now().timestamp()
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = [datetime.fromtimestamp(random.uniform(0.0, max_int)) for _ in range(20)]
        check_value = random.choice(values)
        r_obj = R(**{f"val_array__{op}": ALL(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)
        expected = all([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize("op", ("gt", "gte", "exact", "lt", "lte"))
@pytest.mark.unit
def test_match_any_on_datetime_values(op):
    """Test ANY behavior on a large range of random datetime values."""
    max_int = datetime.now().timestamp()
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = [datetime.fromtimestamp(random.uniform(0.0, max_int)) for _ in range(20)]
        check_value = random.choice(values)
        r_obj = R(**{f"val_array__{op}": ANY(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)
        expected = any([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize(
    "op", ("contains", "icontains", "exact", "iexact", "startswith", "istartswith", "endswith", "iendswith")
)
@pytest.mark.unit
def test_match_all_on_text_values(op):
    """Test ALL behavior on a large range of random text values."""
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = unique_text_array()
        base_check_value = random.choice(values)
        if op in ("startswith", "istartswith"):
            check_value = base_check_value[0:1]
        elif op in ("endswith", "iendswith"):
            check_value = base_check_value[-1]
        elif op in ("contains", "icontains"):
            check_value = base_check_value[2]
        else:
            check_value = base_check_value
        r_obj = R(**{f"val_array__{op}": ALL(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)

        expected = all([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize(
    "op", ("contains", "icontains", "exact", "iexact", "startswith", "istartswith", "endswith", "iendswith")
)
@pytest.mark.unit
def test_match_any_on_text_values(op):
    """Test ANY behavior on a large range of random text values."""
    compare_func = OPERAND_MAP[op]
    for _ in range(30):
        values = unique_text_array()
        base_check_value = random.choice(values)
        if op in ("startswith", "istartswith"):
            check_value = base_check_value[0:1]
        elif op in ("endswith", "iendswith"):
            check_value = base_check_value[-1]
        elif op in ("contains", "icontains"):
            check_value = base_check_value[2]
        else:
            check_value = base_check_value
        r_obj = R(**{f"val_array__{op}": ANY(check_value)})
        fake_obj = FakeObject(0, 0, val_array=values)

        expected = any([compare_func(x, check_value) for x in values])
        actual = r_obj.matches(fake_obj)
        expected == actual, f"{r_obj} match for `{check_value}` expected `{expected}` but returned `{actual}`"


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__startswith=ALL("b")),
        R(val_array__istartswith=ALL("b")),
        R(val_array__contains=ALL("b")),
        R(val_array__isnull=ALL(False)),
    ),
)
@pytest.mark.unit
def test_matching_all_true(r_obj):
    """Validate TRUE matches on a value with an ALL search."""
    fake_obj = FakeObject(3, 4)  # Default val_array is ("boo", "bar", "baz")
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        ~R(val_array__startswith=ALL("b")),
        ~R(val_array__istartswith=ALL("b")),
        ~R(val_array__contains=ALL("b")),
        ~R(val_array__isnull=ALL(False)),
    ),
)
@pytest.mark.unit
def test_matching_all_true_negated(r_obj):
    """Validate TRUE matches on a value with an ALL search yield False when negated."""
    fake_obj = FakeObject(3, 4)  # Default val_array is ("boo", "bar", "baz")
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ALL(2)),
        R(val_array__gte=ALL(2)),
        R(val_array__lt=ALL(26)),
        R(val_array__lte=ALL(26)),
    ),
)
@pytest.mark.unit
def test_matching_all_true_numerical(r_obj):
    """Test matching values using ALL on numerical operations."""
    fake_obj = FakeObject(3, 4, val_array=(4, 5, 9))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__startswith=ALL("b")),
        R(val_array__iendswith=ALL("o")),
        R(val_array__contains=ALL("b")),
        R(val_array__isnull=ALL(True)),
    ),
)
@pytest.mark.unit
def test_matching_all_false(r_obj):
    """Fail a match on a value that's an ALL."""
    fake_obj = FakeObject(3, 4, val_array=("foo", "bar", "baz"))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ALL(5)),
        R(val_array__gte=ALL(5)),
        R(val_array__lt=ALL(8)),
        R(val_array__lte=ALL(8)),
    ),
)
@pytest.mark.unit
def test_matching_all_false_numerical(r_obj):
    """Test failing matches on values using ALL on numerical operations."""
    fake_obj = FakeObject(3, 4, val_array=(4, 5, 9))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__startswith=ANY("b")),
        R(val_array__istartswith=ANY("b")),
        R(val_array__contains=ANY("b")),
        R(val_array__isnull=ANY(False)),
        R(val_array__exact=ANY("baz")),
        R(val_array__endswith=ANY("z")),
    ),
)
@pytest.mark.unit
def test_matching_any_true(r_obj):
    """Validate True matches using ANY."""
    fake_obj = FakeObject(3, 4, val_array=("foo", "bar", "baz"))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gte=ANY(12)),
        R(val_array__gt=ANY(5)),
        R(val_array__exact=ANY(7)),
        R(val_array__isnull=ANY(False)),
        R(val_array__lt=ANY(12)),
        R(val_array__lt=ANY(12)),
    ),
)
@pytest.mark.unit
def test_matching_any_true_numerical(r_obj):
    """Validate True numerical matches using ANY"""
    fake_obj = FakeObject(3, 4, val_array=(5, 7, 12))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__startswith=ANY("z")),
        R(val_array__iendswith=ANY("f")),
        R(val_array__contains=ANY("x")),
        R(val_array__isnull=ANY(True)),
    ),
)
@pytest.mark.unit
def test_matching_any_false(r_obj):
    """Validate False matches using ANY."""
    fake_obj = FakeObject(3, 4, val_array=("foo", "bar", "baz"))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gte=ANY(13)),
        R(val_array__gt=ANY(12)),
        R(val_array__exact=ANY(6)),
        R(val_array__isnull=ANY(True)),
        R(val_array__lt=ANY(5)),
        R(val_array__lte=ANY(4)),
    ),
)
@pytest.mark.unit
def test_matching_any_false_numerical(r_obj):
    """Fail a match on a numerical value that's an ANY."""
    fake_obj = FakeObject(3, 4, val_array=(5, 7, 12))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gte=ANY(13, attr_name="a")),
        R(val_array__gt=ANY(12, attr_name="a")),
        R(val_array__exact=ANY(6, attr_name="a")),
        R(val_array__isnull=ANY(True, attr_name="a")),
        R(val_array__lt=ANY(5, attr_name="a")),
        R(val_array__lte=ANY(4, attr_name="a")),
    ),
)
@pytest.mark.unit
def test_matching_any_false_attr(r_obj):
    """Fail a match on an ANY when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(5, 6), SimpleObj(7, 8), SimpleObj(12, 13)))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gte=ANY(12, attr_name="a")),
        R(val_array__gt=ANY(5, attr_name="a")),
        R(val_array__exact=ANY(7, attr_name="a")),
        R(val_array__isnull=ANY(False, attr_name="a")),
        R(val_array__lt=ANY(12, attr_name="a")),
        R(val_array__lt=ANY(12, attr_name="a")),
    ),
)
@pytest.mark.unit
def test_matching_any_true_attr(r_obj):
    """Validate True match using ANY when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(5, 0), SimpleObj(7, 0), SimpleObj(12, 0)))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ALL(5, attr_name="a")),
        R(val_array__gte=ALL(5, attr_name="a")),
        R(val_array__lt=ALL(8, attr_name="a")),
        R(val_array__lte=ALL(8, attr_name="a")),
    ),
)
@pytest.mark.unit
def test_matching_all_false_attr(r_obj):
    """Fail a match on an ALL when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(4, 0), SimpleObj(5, 0), SimpleObj(9, 0)))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ALL(2, attr_name="b")),
        R(val_array__gte=ALL(2, attr_name="b")),
        R(val_array__lt=ALL(26, attr_name="b")),
        R(val_array__lte=ALL(26, attr_name="b")),
    ),
)
@pytest.mark.unit
def test_matching_all_true_attr(r_obj):
    """Validate True match using ALL when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(0, 4), SimpleObj(0, 5), SimpleObj(0, 9)))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__contains=EXACT_N("b", n=3)),
        R(val_array__icontains=EXACT_N("b", n=3)),
        R(val_array__exact=EXACT_N("boo", n=1)),
        R(val_array__iexact=EXACT_N("boo", n=1)),
        R(val_array__startswith=EXACT_N("b", n=3)),
        R(val_array__istartswith=EXACT_N("b", n=3)),
        R(val_array__endswith=EXACT_N("o", n=1)),
        R(val_array__iendswith=EXACT_N("o", n=1)),
        R(val_array__isnull=EXACT_N(False, n=3)),
    ),
)
@pytest.mark.unit
def test_matching_exact_n_true_string(r_obj):
    """Validate TRUE matches on a value with an EXACT_N search."""
    fake_obj = FakeObject(3, 4)  # Default val_array is ("boo", "bar", "baz")
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=EXACT_N(2, n=3)),
        R(val_array__gte=EXACT_N(2, n=3)),
        R(val_array__lt=EXACT_N(8, n=2)),
        R(val_array__lte=EXACT_N(8, n=2)),
    ),
)
@pytest.mark.unit
def test_matching_exact_n_true_numerical(r_obj):
    """Test matching values using EXACT_N on numerical operations."""
    fake_obj = FakeObject(3, 4, val_array=(4, 5, 9))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__contains=EXACT_N("b", n=2)),
        R(val_array__icontains=EXACT_N("b", n=2)),
        R(val_array__exact=EXACT_N("boo", n=2)),
        R(val_array__iexact=EXACT_N("boo", n=2)),
        R(val_array__startswith=EXACT_N("b", n=2)),
        R(val_array__istartswith=EXACT_N("b", n=2)),
        R(val_array__endswith=EXACT_N("o", n=2)),
        R(val_array__iendswith=EXACT_N("o", n=2)),
        R(val_array__isnull=EXACT_N(False, n=2)),
    ),
)
@pytest.mark.unit
def test_matching_exact_n_false(r_obj):
    """Fail a match on a value that's an EXACT_N."""
    fake_obj = FakeObject(3, 4, val_array=("foo", "bar", "baz"))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=EXACT_N(2, n=2)),
        R(val_array__gte=EXACT_N(2, n=2)),
        R(val_array__lt=EXACT_N(8, n=3)),
        R(val_array__lte=EXACT_N(8, n=3)),
    ),
)
@pytest.mark.unit
def test_matching_exact_n_false_numerical(r_obj):
    """Test failing matches on values using EXACT_N on numerical operations."""
    fake_obj = FakeObject(3, 4, val_array=(4, 5, 9))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=EXACT_N(3, attr_name="b", n=2)),
        R(val_array__gte=EXACT_N(3, attr_name="b", n=2)),
        R(val_array__lt=EXACT_N(10, attr_name="b", n=2)),
        R(val_array__lte=EXACT_N(10, attr_name="b", n=2)),
    ),
)
@pytest.mark.unit
def test_matching_exact_n_false_attr(r_obj):
    """Validate True match using EXACT_N when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(0, 4), SimpleObj(0, 5), SimpleObj(0, 9)))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=EXACT_N(3, attr_name="b", n=3)),
        R(val_array__gte=EXACT_N(3, attr_name="b", n=3)),
        R(val_array__lt=EXACT_N(6, attr_name="b", n=2)),
        R(val_array__lte=EXACT_N(6, attr_name="b", n=2)),
    ),
)
@pytest.mark.unit
def test_matching_exact_n_true_attr(r_obj):
    """Validate True match using EXACT_N when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(0, 4), SimpleObj(0, 5), SimpleObj(0, 9)))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.unit
def test_matching_exact_n_too_short():
    fake_obj = FakeObject(3, 4, val_array=(3, 3, 3))
    rule_obj = R(val_array__exact=EXACT_N(3, n=4))
    assertRuleNotMatches(rule_obj, fake_obj)


@pytest.mark.unit
def test_matching_exact_n_not_consecutive():
    fake_obj = FakeObject(3, 4, val_array=(3, 2, 3))
    rule_obj = R(val_array__exact=EXACT_N(3, n=3))
    assertRuleNotMatches(rule_obj, fake_obj)


@pytest.mark.unit
def test_matching_exact_n_too_many_matching():
    fake_obj = FakeObject(3, 4, val_array=(3, 3, 3))
    rule_obj = R(val_array__exact=EXACT_N(3, n=2))
    assertRuleNotMatches(rule_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__contains=ATLEAST("b", n=2)),
        R(val_array__icontains=ATLEAST("b", n=2)),
        R(val_array__exact=ATLEAST("boo", n=1)),
        R(val_array__iexact=ATLEAST("boo", n=1)),
        R(val_array__startswith=ATLEAST("b", n=2)),
        R(val_array__istartswith=ATLEAST("b", n=2)),
        R(val_array__endswith=ATLEAST("o", n=1)),
        R(val_array__iendswith=ATLEAST("o", n=1)),
        R(val_array__isnull=ATLEAST(False, n=2)),
    ),
)
@pytest.mark.unit
def test_matching_atleast_true_string(r_obj):
    """Validate TRUE matches on a value with an ATLEAST search."""
    fake_obj = FakeObject(3, 4)  # Default val_array is ("boo", "bar", "baz")
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ATLEAST(2, n=2)),
        R(val_array__gte=ATLEAST(2, n=2)),
        R(val_array__lt=ATLEAST(8, n=2)),
        R(val_array__lte=ATLEAST(8, n=2)),
    ),
)
@pytest.mark.unit
def test_matching_atleast_true_numerical(r_obj):
    """Test matching values using ATLEAST on numerical operations."""
    fake_obj = FakeObject(3, 4, val_array=(4, 5, 9))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__contains=ATLEAST("b", n=2)),
        R(val_array__icontains=ATLEAST("b", n=2)),
        R(val_array__exact=ATLEAST("boo", n=2)),
        R(val_array__iexact=ATLEAST("boo", n=2)),
        R(val_array__startswith=ATLEAST("b", n=2)),
        R(val_array__istartswith=ATLEAST("b", n=2)),
        R(val_array__endswith=ATLEAST("o", n=2)),
        R(val_array__iendswith=ATLEAST("o", n=2)),
        R(val_array__isnull=ATLEAST(False, n=4)),
    ),
)
@pytest.mark.unit
def test_matching_atleast_false(r_obj):
    """Fail a match on a value that's an ATLEAST."""
    fake_obj = FakeObject(3, 4, val_array=("foo", "bar", "baz"))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ATLEAST(2, n=4)),
        R(val_array__gte=ATLEAST(2, n=4)),
        R(val_array__lt=ATLEAST(8, n=3)),
        R(val_array__lte=ATLEAST(8, n=3)),
    ),
)
@pytest.mark.unit
def test_matching_atleast_false_numerical(r_obj):
    """Test failing matches on values using ATLEAST on numerical operations."""
    fake_obj = FakeObject(3, 4, val_array=(4, 5, 9))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ATLEAST(3, attr_name="b", n=4)),
        R(val_array__gte=ATLEAST(3, attr_name="b", n=4)),
        R(val_array__lt=ATLEAST(10, attr_name="b", n=4)),
        R(val_array__lte=ATLEAST(10, attr_name="b", n=4)),
    ),
)
@pytest.mark.unit
def test_matching_atleast_false_attr(r_obj):
    """Validate True match using ATLEAST when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(0, 4), SimpleObj(0, 5), SimpleObj(0, 9)))
    assertRuleNotMatches(r_obj, fake_obj)


@pytest.mark.parametrize(
    "r_obj",
    (
        R(val_array__gt=ATLEAST(3, attr_name="b", n=3)),
        R(val_array__gte=ATLEAST(3, attr_name="b", n=3)),
        R(val_array__lt=ATLEAST(6, attr_name="b", n=2)),
        R(val_array__lte=ATLEAST(6, attr_name="b", n=2)),
    ),
)
@pytest.mark.unit
def test_matching_atleast_true_attr(r_obj):
    """Validate True match using ATLEAST when the lookup value is a sub-attribute."""
    fake_obj = FakeObject(3, 4, val_array=(SimpleObj(0, 4), SimpleObj(0, 5), SimpleObj(0, 9)))
    assertRuleMatches(r_obj, fake_obj)


@pytest.mark.unit
def test_matching_atleast_too_short():
    fake_obj = FakeObject(3, 4, val_array=(3, 3, 3))
    rule_obj = R(val_array__exact=ATLEAST(3, n=4))
    assertRuleNotMatches(rule_obj, fake_obj)


@pytest.mark.unit
def test_matching_atleast_not_consecutive():
    fake_obj = FakeObject(3, 4, val_array=(3, 2, 3))
    rule_obj = R(val_array__exact=ATLEAST(3, n=2))
    assertRuleNotMatches(rule_obj, fake_obj)


@pytest.mark.unit
def test_matching_atleast_more_matching():
    fake_obj = FakeObject(3, 4, val_array=(3, 3, 3))
    rule_obj = R(val_array__exact=ATLEAST(3, n=2))
    assertRuleMatches(rule_obj, fake_obj)


@pytest.mark.unit
def test_matching_r_value():
    fake_obj = FakeObject(
        SimpleObj(1, 2),
        3,
        val_array=(
            SimpleObj([SimpleObj("x", 0), SimpleObj("y", 0)], 0),
            SimpleObj([SimpleObj("x", 0), SimpleObj("x", 0)], 0),
        ),
    )

    assertRuleMatches(R(a__r=R(b__exact=2)), fake_obj)
    assertRuleMatches(R(val_array__r=ALL(R(a__exact=ANY("x", attr_name="a")))), fake_obj)
    assertRuleMatches(R(val_array__r=EXACT_N(R(a__exact=ANY("y", attr_name="a")), n=1)), fake_obj)
    assertRuleMatches(R(val_array__r=ATLEAST(R(a__exact=ANY("x", attr_name="a")), n=2)), fake_obj)

    assertRuleNotMatches(R(a__r=R(b__exact=1)), fake_obj)
    assertRuleNotMatches(R(val_array__r=ALL(R(a__exact=ANY("missing", attr_name="a")))), fake_obj)
    assertRuleNotMatches(R(val_array__r=EXACT_N(R(a__exact=ANY("y", attr_name="a")), n=2)), fake_obj)
    assertRuleNotMatches(R(val_array__r=ATLEAST(R(a__exact=ANY("x", attr_name="a")), n=3)), fake_obj)
