from datetime import datetime, timezone, UTC
from uuid import uuid4

import pytest
from marshmallow import ValidationError
from werkzeug.datastructures import MultiDict

from common.entities import InstanceStatus
from common.entity_services.helpers import RunFilters, UpcomingInstanceFilters
from common.entity_services.helpers.filter_rules import (
    END_RANGE_BEGIN_QUERY_NAME,
    END_RANGE_END_QUERY_NAME,
    END_RANGE_QUERY_NAME,
    JOURNEY_ID_QUERY_NAME,
    JOURNEY_NAMES_QUERY_NAME,
    START_RANGE_BEGIN_QUERY_NAME,
    START_RANGE_END_QUERY_NAME,
    START_RANGE_QUERY_NAME,
    Filters,
    ProjectEventFilters,
    _date_or_none,
    _str_to_bool,
)


@pytest.mark.unit
def test_filters_not_implemented():
    with pytest.raises(NotImplementedError):
        Filters.from_params(MultiDict([]))


@pytest.mark.unit
def test_date_or_none():
    assert _date_or_none(MultiDict(), "a") is None
    assert isinstance(_date_or_none(MultiDict([("a", "2022-08-16")]), "a"), datetime)
    assert isinstance(_date_or_none(MultiDict([("a", "2022-08-16T17:57:23.453573+00:00")]), "a"), datetime)

    with pytest.raises(ValidationError, match="b"):
        _date_or_none(MultiDict([("b", "invalid date")]), "b")


@pytest.mark.unit
def test_run_filters_str_to_bool():
    # most of this testing is handled in request_parsings str_to_bool implementation.
    assert _str_to_bool(MultiDict([("a", "true")]), "a") is True
    assert _str_to_bool(MultiDict([("a", "false")]), "a") is False
    assert _str_to_bool(MultiDict([("a", None)]), "a") is None


@pytest.mark.unit
def test_from_params_start():
    # we currently ignore unknown query parameters in our rules objects. A couple of other queries are
    # tossed in just to test.
    start = MultiDict(
        [("page", "5"), ("count", "25"), ("start_range_begin", "2022-08-16"), ("start_range_end", "2022-08-17")]
    )
    filters = RunFilters.from_params(start)

    # We want to see that arrow is giving us the kind of timestamp we think; i.e., a UTC aware
    # timestamp.
    assert filters.start_range_begin == datetime(year=2022, month=8, day=16, tzinfo=UTC)
    assert filters.start_range_end == datetime(year=2022, month=8, day=17, tzinfo=UTC)
    assert filters.end_range_begin is None
    assert filters.end_range_end is None
    assert bool(filters)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("range_name_begin, range_name_end"),
    (
        (START_RANGE_BEGIN_QUERY_NAME, START_RANGE_END_QUERY_NAME),
        (END_RANGE_BEGIN_QUERY_NAME, END_RANGE_END_QUERY_NAME),
    ),
)
def test_invalid_time_range(range_name_begin, range_name_end):
    data = MultiDict([("page", "5"), ("count", "25"), (range_name_begin, "2022-08-18"), (range_name_end, "2022-08-17")])
    with pytest.raises(ValidationError):
        RunFilters.from_params(data)


@pytest.mark.unit
@pytest.mark.parametrize("filter_class", [ProjectEventFilters])
def test_invalid_event_type(filter_class):
    data = MultiDict([("event_type", "InvalidEventType")])
    with pytest.raises(ValidationError):
        filter_class.from_params(data)


@pytest.mark.unit
@pytest.mark.parametrize("filter_class", [ProjectEventFilters])
def test_valid_event_type(filter_class):
    filters = filter_class.from_params(
        MultiDict([("event_type", "BATCH_PIPELINE_STATUS"), ("event_type", "TEST_OUTCOMES")])
    )
    assert filters.event_types == ["BATCH_PIPELINE_STATUS", "TEST_OUTCOMES"]


@pytest.mark.unit
def test_run_filters_from_parameters_end():
    end = MultiDict(
        [("page", "5"), ("count", "25"), ("end_range_begin", "2022-08-16"), ("end_range_end", "2022-08-17")]
    )
    filters = RunFilters.from_params(end)
    assert filters.end_range_begin == datetime(year=2022, month=8, day=16, tzinfo=UTC)
    assert filters.end_range_end == datetime(year=2022, month=8, day=17, tzinfo=UTC)
    assert filters.start_range_begin is None
    assert filters.start_range_end is None
    assert filters.pipeline_keys == []
    assert filters.run_keys == []
    assert bool(filters)


@pytest.mark.unit
def test_run_filters_from_parameters_none():
    end = MultiDict([("page", "5"), ("count", "25")])
    filters = RunFilters.from_params(end)
    assert filters.end_range_begin is None
    assert filters.end_range_end is None
    assert filters.start_range_begin is None
    assert filters.start_range_end is None
    assert filters.pipeline_keys == []
    assert filters.run_keys == []
    assert not bool(filters)


@pytest.mark.unit
def test_run_filters_from_parameters_names():
    end = MultiDict(
        [("page", "5"), ("count", "25"), ("pipeline_key", "foo"), ("pipeline_key", "bar"), ("pipeline_key", "baz")]
    )
    filters = RunFilters.from_params(end)
    assert filters.end_range_begin is None
    assert filters.end_range_end is None
    assert filters.start_range_begin is None
    assert filters.start_range_end is None
    assert sorted(filters.pipeline_keys) == sorted(["foo", "bar", "baz"])
    assert bool(filters)


@pytest.mark.unit
def test_run_filters_from_parameters_run_keys():
    end = MultiDict([("page", "5"), ("count", "25"), ("run_key", "foo"), ("run_key", "bar"), ("run_key", "baz")])
    filters = RunFilters.from_params(end)
    assert filters.end_range_begin is None
    assert filters.end_range_end is None
    assert filters.start_range_begin is None
    assert filters.start_range_end is None
    assert filters.pipeline_keys == []
    assert sorted(filters.run_keys) == sorted(["foo", "bar", "baz"])
    assert bool(filters)


@pytest.mark.unit
def test_filters_invalid_event_types():
    Filters.validate_event_types(["BATCH_PIPELINE_STATUS"])

    with pytest.raises(ValidationError):
        Filters.validate_event_types(["INVALID_EVENT_TYPE"])


@pytest.mark.unit
def test_filters_invalid_instance_status():
    Filters.validate_instance_status([InstanceStatus.ACTIVE.value])

    with pytest.raises(ValidationError):
        Filters.validate_instance_status(["RANDOM"])


@pytest.mark.unit
def test_upcoming_instances_filters_valid():
    params = MultiDict(
        [
            (START_RANGE_QUERY_NAME, "2022-08-16"),
            (END_RANGE_QUERY_NAME, "2022-08-17"),
            (JOURNEY_ID_QUERY_NAME, uuid4()),
            (JOURNEY_NAMES_QUERY_NAME, "journey name"),
        ]
    )
    filters = UpcomingInstanceFilters.from_params(params)
    assert filters.start_range is not None
    assert filters.end_range is not None
    assert len(filters.journey_ids) == 1
    assert len(filters.journey_names) == 1


@pytest.mark.unit
@pytest.mark.parametrize(
    ("range"),
    (
        [
            (START_RANGE_QUERY_NAME, "2022-08-16"),
            (END_RANGE_QUERY_NAME, "2022-08-14"),
        ],
        [
            (END_RANGE_QUERY_NAME, "2022-08-14"),
        ],
    ),
)
def test_upcoming_instances_filters_invalid_time_ranges(range):
    params = MultiDict(range)
    with pytest.raises(ValidationError):
        UpcomingInstanceFilters.from_params(params)
