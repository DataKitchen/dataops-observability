from uuid import UUID

import pytest

from common.datetime_utils import datetime_to_timestamp
from observability_api.schemas import InstanceAlertSchema, RunAlertSchema
from testlib.fixtures import entities
from testlib.fixtures.entities import ALERT_EXPECTED_END_DT, ALERT_EXPECTED_START_DT

instance_alert_entity = entities.instance_alert
run_alert_entity = entities.run_alert


@pytest.mark.unit
def test_instance_alert_dump(instance_alert_entity):
    data = InstanceAlertSchema().dump(instance_alert_entity)

    assert "instance-alert-1" == data["name"]
    assert datetime_to_timestamp(ALERT_EXPECTED_START_DT) == data["details"]["expected_start_time"]
    assert datetime_to_timestamp(ALERT_EXPECTED_END_DT) == data["details"]["expected_end_time"]

    try:
        UUID(data["id"])
    except Exception:
        raise AssertionError(f"ID {data['id']} is not a valid UUID")


@pytest.mark.unit
def test_run_alert_dump(run_alert_entity):
    data = RunAlertSchema().dump(run_alert_entity)

    assert "run-alert-1" == data["name"]
    assert datetime_to_timestamp(ALERT_EXPECTED_START_DT) == data["details"]["expected_start_time"]
    assert datetime_to_timestamp(ALERT_EXPECTED_END_DT) == data["details"]["expected_end_time"]

    try:
        UUID(data["id"])
    except Exception:
        raise AssertionError(f"ID {data['id']} is not a valid UUID")
