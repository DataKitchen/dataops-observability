import pytest

from common.entities import InstanceAlert as InstanceAlertEntity
from common.entities import RunAlert as RunAlertEntity
from testlib.fixtures import entities, v2_events

# This works around the import shenanigans for pytest; importing the module wholesale then assigning what
# we need avoids all of the from testlib.fixtures import *  stuff while also allowing use to be explicit
# about what fixtures we need.
run_alert_entity = entities.run_alert
instance_alert_entity = entities.instance_alert
run_alert = v2_events.run_alert
instance_alert = v2_events.instance_alert


@pytest.mark.integration
def test_run_alert_alert_prop(run_alert, run_alert_entity):
    """RunAlert `alert` property returns associated RunAlert."""
    alert_obj = run_alert.alert

    assert run_alert.alert_id == alert_obj.id
    assert isinstance(alert_obj, RunAlertEntity)


@pytest.mark.integration
def test_instance_alert_alert_prop(instance_alert, instance_alert_entity):
    """InstanceAlert `alert` property returns associated InstanceAlert."""
    alert_obj = instance_alert.alert

    assert instance_alert.alert_id == alert_obj.id
    assert isinstance(alert_obj, InstanceAlertEntity)
