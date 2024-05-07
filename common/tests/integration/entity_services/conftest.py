from datetime import datetime, timezone

import pytest

from common.entities import JourneyDagEdge, Pipeline, Run, RunStatus, TestOutcome
from common.events.v1 import TestOutcomesEvent, TestStatuses
from testlib.fixtures.entities import *
from testlib.fixtures.internal_events import *
from testlib.fixtures.v1_events import *


@pytest.fixture()
def pipeline_2(test_db, project):
    return Pipeline.create(key="P2", project=project)


@pytest.fixture()
def pipeline_3(test_db, project):
    return Pipeline.create(key="P3", project=project)


@pytest.fixture()
def pipeline_4(test_db, project):
    return Pipeline.create(key="P4", project=project)


@pytest.fixture
def current_time() -> datetime:
    yield datetime.now(timezone.utc)


@pytest.fixture()
def journey_dag_edges(test_db, journey, pipeline, pipeline_2, pipeline_3):
    # 3 node dag
    # pipeline -> pipeline_2
    # pipeline -> pipeline_3
    return [
        JourneyDagEdge.create(journey=journey, left=pipeline_2, right=pipeline),
        JourneyDagEdge.create(journey=journey, right=pipeline_2),
        JourneyDagEdge.create(journey=journey, left=pipeline_3, right=pipeline),
        JourneyDagEdge.create(journey=journey, right=pipeline_3),
    ]


@pytest.fixture
def run(test_db, pipeline):
    return Run.create(key=run_key, pipeline=pipeline, status=RunStatus.RUNNING.name, id=run_id)


@pytest.fixture
def test_outcomes_instance(test_db, run, pipeline, instance_instance_set):
    common_data = dict(component=pipeline, run=run, instance_set=instance_instance_set.instance_set)
    return [
        TestOutcome.create(**common_data, name="TO1", status=TestStatuses.PASSED.name),
        TestOutcome.create(**common_data, name="TO2", status=TestStatuses.PASSED.name),
        TestOutcome.create(**common_data, name="TO3", status=TestStatuses.PASSED.name),
        TestOutcome.create(**common_data, name="TO4", status=TestStatuses.WARNING.name),
        TestOutcome.create(**common_data, name="TO5", status=TestStatuses.WARNING.name),
    ]


@pytest.fixture
def test_outcomes_event(project, pipeline, run, event_data):
    timestamp = datetime.now(timezone.utc).isoformat()
    data = {
        "event_type": TestOutcomesEvent.__name__,
        "test_outcomes": [
            {
                "name": f"test outcome {i}",
                "status": TestStatuses.PASSED.name,
                "start_time": timestamp,
                "end_time": timestamp,
                "metadata": {"favorite_color": "blue"},
                "metric_value": 12 * i,
                "min_threshold": -25.5,
                "max_threshold": 25.5,
            }
            for i in range(5)
        ],
    }
    return TestOutcomesEvent(**TestOutcomesEvent.__schema__().load({**event_data, **data}))
