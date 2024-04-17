from unittest.mock import Mock

import pytest
from werkzeug.datastructures import MultiDict

from common.entity_services.helpers import DEFAULT_COUNT, DEFAULT_PAGE, ListRules, Page, SortOrder


@pytest.fixture()
def mocked_field():
    field = Mock()
    yield field


@pytest.fixture()
def mocked_entity_class():
    entity_class = Mock()
    yield entity_class


@pytest.fixture()
def mocked_query():
    # .paginate() (and other query methods in general) doesn't return a list until iterated on, but this is good enough for the test
    paginate = Mock(return_value=list())
    query = Mock()
    query.paginate = paginate
    query.order_by = Mock(return_value=query)
    yield query


@pytest.fixture()
def mocked_query_with_data():
    # .paginate() (and other query methods in general) doesn't return a list until iterated on, but this is good enough for the test
    paginate = Mock(return_value=[Mock(), Mock()])
    query = Mock()
    query.paginate = paginate
    query.order_by = Mock(return_value=query)
    yield query


@pytest.mark.unit
def test_from_params():
    rules = ListRules.from_params(MultiDict([("page", "5"), ("count", "25"), ("sort", "desc")]))
    assert rules.page == 5
    assert rules.count == 25
    assert rules.sort == SortOrder.DESC


@pytest.mark.unit
def test_from_params_defaults():
    rules = ListRules.from_params(MultiDict())
    assert rules.page == DEFAULT_PAGE
    assert rules.count == DEFAULT_COUNT
    assert rules.sort == SortOrder.ASC


@pytest.mark.unit
def test_order_by_field_asc(mocked_field):
    rules = ListRules.from_params(MultiDict())
    order_by = rules.order_by_field(mocked_field)
    assert order_by == mocked_field.asc()


@pytest.mark.unit
def test_order_by_field_desc(mocked_field):
    rules = ListRules.from_params(MultiDict([("page", "5"), ("count", "25"), ("sort", "desc")]))
    order_by = rules.order_by_field(mocked_field)
    assert order_by == mocked_field.desc()


@pytest.mark.unit
def test_from_params_extras():
    rules = ListRules.from_params(
        MultiDict([("page", "5"), ("count", "25"), ("sort", "desc"), ("foo", "bar"), ("baz", "bat")])
    )
    assert rules.page == 5
    assert rules.count == 25
    assert rules.sort == SortOrder.DESC


@pytest.mark.unit
def test_page_get_paginated_results(mocked_field, mocked_entity_class, mocked_query):
    rules = ListRules.from_params(MultiDict())
    result = Page[mocked_entity_class].get_paginated_results(mocked_query, mocked_field, rules)
    mocked_field.asc.assert_called_once()
    mocked_query.paginate.assert_called_once()
    mocked_query.count.assert_called_once()
    assert type(result) == Page


@pytest.mark.unit
def test_page_len(mocked_field, mocked_entity_class, mocked_query_with_data):
    rules = ListRules.from_params(MultiDict())
    result = Page[mocked_entity_class].get_paginated_results(mocked_query_with_data, mocked_field, rules)
    assert len(result) == 2
    # Assert that the length is tied to the length of result, not the count()/total of the query.
    result.results.clear()
    assert len(result) == 0


@pytest.mark.unit
def test_page_iter(mocked_field, mocked_entity_class, mocked_query_with_data):
    rules = ListRules.from_params(MultiDict())
    result = Page[mocked_entity_class].get_paginated_results(mocked_query_with_data, mocked_field, rules)
    count = len(mocked_query_with_data.paginate())
    r = [r for r in result]
    assert len(r) == count
