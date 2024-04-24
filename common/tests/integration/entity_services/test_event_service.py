import contextlib
from unittest.mock import patch

import pytest

from common.entities import DB
from common.entity_services import EventService
from common.entity_services.helpers import ListRules, ProjectEventFilters, SortOrder
from testlib.fixtures.entities import *


@contextlib.contextmanager
def assert_num_queries(num):
    with patch.object(DB.obj, "execute_sql", wraps=DB.obj.execute_sql) as mock:
        yield mock
    assert mock.call_count == num


@pytest.mark.integration
def test_get_events_with_rules_filters(
    event_entity, event_entity_2, project, pipeline, instance_instance_set, run, task
):
    filter_cases = (
        ({}, (event_entity, event_entity_2)),
        ({"component_id": [str(pipeline.id)]}, (event_entity,)),
        ({"instance_id": [str(instance_instance_set.instance_id)]}, (event_entity,)),
        ({"journey_id": [str(instance_instance_set.instance.journey_id)]}, (event_entity,)),
        ({"event_type": ["BATCH_PIPELINE_STATUS"]}, (event_entity,)),
        ({"event_type": ["DATASET_OPERATION"]}, (event_entity_2,)),
        ({"event_id": [str(event_entity_2.id)]}, (event_entity_2,)),
        ({"run_id": [str(run.id)]}, (event_entity,)),
        ({"task_id": [str(task.id)]}, (event_entity,)),
        ({"date_range_start": "2024-01-20T09:56:00"}, (event_entity,)),
        ({"date_range_end": "2024-01-20T09:59:10"}, (event_entity, event_entity_2)),
        (
            {"date_range_start": "2024-01-20T09:56:00", "date_range_end": "2024-01-20T09:59:10"},
            (event_entity,),
        ),
        # Not considering the created_timestamp when timestamp is present
        ({"date_range_start": "2024-01-20T09:59:10"}, ()),
    )

    rules = ListRules()
    for filter_params, expected_result in filter_cases:
        filters = ProjectEventFilters.from_params(params=filter_params, project_ids=[project.id])
        page = EventService.get_events_with_rules(rules=rules, filters=filters)
        assert set(page.results) == set(expected_result), filter_params


@pytest.mark.integration
@pytest.mark.parametrize("sort_order,reverse", ((SortOrder.ASC, False), (SortOrder.DESC, True)))
def test_get_events_with_rules_sort(sort_order, reverse, event_entity, event_entity_2, project):
    rules = ListRules(sort=sort_order)
    filters = ProjectEventFilters.from_params(params={}, project_ids=[project.id])

    page = EventService.get_events_with_rules(rules=rules, filters=filters)

    expected = [event_entity, event_entity_2] if reverse else [event_entity_2, event_entity]
    assert page.results == expected


@pytest.mark.integration
def test_get_events_with_rules_prefetch(event_entity, project, instance):
    rules = ListRules()
    filters = ProjectEventFilters.from_params(params={}, project_ids=[project.id])

    with assert_num_queries(3):
        (result_event,) = EventService.get_events_with_rules(rules=rules, filters=filters)

    with assert_num_queries(0):
        assert result_event.component is not None
        assert result_event.run is not None
        assert result_event.task is not None
        assert result_event.run_task is not None
        assert len(result_event.instances) == 1
        assert result_event.instances[0]["instance"].id == instance.id
        assert result_event.instances[0]["journey"].id == instance.journey_id
