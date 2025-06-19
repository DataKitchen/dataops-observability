from typing import Any, Optional

from common.predicate_engine.query import ALL, ANY, R


def assertRuleEqual(a, b, default_op="exact"):
    """A custom assertion that can compare the value of two Rule (R) object intances."""
    # False if they aren't Rule objects at all then fail
    if not isinstance(a, R) or not isinstance(b, R):
        raise AssertionError("Cannot compare non-R objects.")

    if a.negated and not b.negated:
        raise AssertionError("Rules differ: negated=True != negated=False")

    if not a.negated and b.negated:
        raise AssertionError("Rules differ: negated=False != negated=True")

    def _to_str(value):
        """
        Normalize the value to a string with it's attributes sorted.

        This will recursively descend through an R object, adding in default operators when omitted. For example if
        you have something like R(a=True) then it'll first be normalized to R(a__exact=True) so that those two
        values can be compared.
        """
        if isinstance(value, tuple):
            if "__" not in value[0]:
                # Add the default query operand if it was omitted
                return str((f"{value[0]}__{default_op}", value[1]))
            elif isinstance(value[1], ANY | ALL):
                return f"{str(value[0])}, {str(value[1])}"
            else:
                return str(value)

        if value.negated:
            return f"(NOT ({value.conn_type.name}: {', '.join(sorted([_to_str(x) for x in value.children]))}))"
        return f"({value.conn_type.name}: {', '.join(sorted([_to_str(x) for x in value.children]))})"

    str_a = _to_str(a)
    str_b = _to_str(b)
    if str_a != str_b:
        raise AssertionError(f"Rules differ: \n\t{str_a}\n\t!=\n\t{str_b}")


def assertRuleMatches(a: R, b: Any, msg: str | None = None):
    """Assert that an R object matches a given value."""
    try:
        result = a.matches(b)
    except Exception as e:
        raise AssertionError(msg or f"R object `{a}` failed to match value `{b}`.") from e
    else:
        if result is False:
            raise AssertionError(msg or f"R object `{a}` failed to match value `{b}`.")

    # Anytime a rule matches, it's inverse should NOT match
    neg_a = ~a
    try:
        result = neg_a.matches(b)
    except Exception:
        pass
    else:
        if result is True:
            raise AssertionError(
                msg or f"R object `{neg_a}` (negation of rule `{a}`) unexpectedly matched value `{b}`."
            )


def assertRuleNotMatches(a: R, b: Any, msg: str | None = None):
    try:
        result = a.matches(b)
    except Exception:
        pass
    else:
        if result is True:
            raise AssertionError(msg or f"R object `{a}` unexpectedly matched value `{b}`.")

    # Anytime a rule does not match, it's inverse SHOULD match
    neg_a = ~a
    try:
        result = neg_a.matches(b)
    except Exception as e:
        raise AssertionError(msg or f"R object `{neg_a}` (negation of rule `{a}`) failed to match value `{b}`.") from e
    else:
        if result is False:
            raise AssertionError(msg or f"R object `{neg_a}` (negation of rule `{a}`) failed to match value `{b}`.")
