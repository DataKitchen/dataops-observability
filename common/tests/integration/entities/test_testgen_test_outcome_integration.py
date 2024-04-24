import pytest
from peewee import IntegrityError

from common.entities import TestGenTestOutcomeIntegration


@pytest.mark.integration
def test_test_outcome_integration(test_outcome):
    inst = TestGenTestOutcomeIntegration.create(
        test_outcome=test_outcome,
        columns=["a", "b", "c"],
        test_suite="some-test",
        version=4,
        table="my-table",
        test_parameters=[{"a": 1}, {"a": 3}],
    )
    assert inst
    inst.save()


@pytest.mark.integration
def test_test_outcome_integration_missing_version(test_outcome):
    with pytest.raises(IntegrityError):
        TestGenTestOutcomeIntegration.create(
            test_outcome=test_outcome,
            columns=["a", "b", "c"],
            test_suite="some-test",
            table="my-table",
        )


@pytest.mark.integration
def test_test_outcome_integration_missing_table(test_outcome):
    with pytest.raises(IntegrityError):
        TestGenTestOutcomeIntegration.create(
            test_outcome=test_outcome,
            columns=["a", "b", "c"],
            test_suite="some-test",
            version=4,
        )


@pytest.mark.integration
def test_test_outcome_integration_missing_test_suite(test_outcome):
    with pytest.raises(IntegrityError):
        TestGenTestOutcomeIntegration.create(
            test_outcome=test_outcome,
            columns=["a", "b", "c"],
            version=4,
            table="my-table",
        )


@pytest.mark.integration
def test_test_outcome_integration_invalid_test_parameters(test_outcome):
    with pytest.raises(ValueError):
        TestGenTestOutcomeIntegration.create(
            test_outcome=test_outcome,
            columns=["a", "b", "c"],
            test_suite="some-test",
            version=4,
            table="my-table",
            test_parameters=["a", "b", "c"],
        )


@pytest.mark.integration
def test_test_outcome_integration_invalid_columns(test_outcome):
    with pytest.raises(ValueError):
        TestGenTestOutcomeIntegration.create(
            test_outcome=test_outcome,
            columns=[1, 2],
            test_suite="some-test",
            version=4,
            table="my-table",
        )
