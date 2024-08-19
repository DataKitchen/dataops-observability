from unittest.mock import ANY, Mock, MagicMock

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
    query = Mock()
    subquery = Mock()
    results_query = MagicMock()

    query.model.select.return_value = subquery
    query.clone = Mock(return_value=results_query)

    subquery.where.return_value = subquery
    subquery.order_by.return_value = subquery
    subquery.paginate.return_value = subquery
    subquery.alias.return_value = subquery

    results_query.join.return_value = results_query
    results_query.order_by.return_value = results_query

    yield query


@pytest.fixture()
def mocked_query_with_data(mocked_query):
    query = mocked_query
    results_query = query.clone.return_value
    results_query.__iter__.return_value = [Mock(), Mock()]
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
    mocked_subquery = mocked_query.model.select.return_value
    mocked_results_query = mocked_query.clone.return_value
    rules = ListRules.from_params(MultiDict())

    result = Page[mocked_entity_class].get_paginated_results(mocked_query, mocked_field, rules)

    mocked_field.asc.assert_called_once()

    mocked_subquery.where.assert_called_once_with(mocked_query._where)
    mocked_subquery.order_by.assert_called_once_with(rules.order_by_field(mocked_field))
    mocked_subquery.paginate.assert_called_once_with(rules.page, rules.count)
    mocked_subquery.alias.assert_called_once()
    mocked_subquery.count.assert_called_once_with(clear_limit=True)

    assert mocked_results_query._where is None
    mocked_results_query.join.assert_called_once_with(mocked_subquery, join_type=ANY, on=ANY)
    mocked_results_query.order_by.assert_called_once_with(rules.order_by_field(mocked_field))

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
    count = len(list(mocked_query_with_data.clone.return_value))
    r = [r for r in result]
    assert len(r) == count
