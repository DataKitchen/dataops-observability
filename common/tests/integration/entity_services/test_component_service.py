from datetime import datetime, timedelta

import pytest

from common.entities import Instance, Journey, JourneyDagEdge
from common.entity_services import ComponentService


@pytest.mark.integration
@pytest.mark.parametrize(
    "create_right,create_left",
    ((True, False), (False, True), (False, False), (True, True)),
    ids=("right edge", "left edge", "no edges", "both edges"),
)
def test_select_journeys(create_right, create_left, test_db, dataset, pipeline, journey):
    if create_right:
        JourneyDagEdge.create(journey=journey, right=dataset)
    if create_left:
        JourneyDagEdge.create(journey=journey, left=dataset, right=pipeline)

    journeys = list(ComponentService.select_journeys(dataset))

    if not create_right and not create_left:
        assert len(journeys) == 0
    else:
        assert len(journeys) == 1
        assert journeys[0] == journey


@pytest.mark.integration
def test_get_or_create_instances(test_db, project, journey, dataset, dag_simple, instance):
    journey_2 = Journey.create(project=project)
    JourneyDagEdge.create(journey=journey_2, right=dataset)

    # Inactive instances shouldn't be considered
    inactive_instances = [
        Instance.create(
            journey=j,
            start_time=datetime.utcnow() - timedelta(minutes=60),
            end_time=datetime.utcnow() - timedelta(minutes=30),
        )
        for j in (journey, journey_2)
    ]

    instances = list(ComponentService.get_or_create_active_instances(dataset))

    assert len(instances) == 2
    instances_dict = dict(instances)
    assert instances_dict[False] == instance
    assert instances_dict[True].end_time is None
    assert instances_dict[True] not in inactive_instances
