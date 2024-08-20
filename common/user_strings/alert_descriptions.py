__all__ = ["RUN_ALERT_DESCRIPTIONS", "INSTANCE_ALERT_DESCRIPTIONS"]

from common.entities import InstanceAlertType, RunAlertType

RUN_ALERT_DESCRIPTIONS: dict[RunAlertType, str] = {
    RunAlertType.LATE_END: "Batch pipeline '{name}' ended late",
    RunAlertType.LATE_START: "Batch pipeline '{name}' started late",
    RunAlertType.MISSING_RUN: "Batch pipeline '{name}' run missed",
    RunAlertType.COMPLETED_WITH_WARNINGS: "Batch pipeline '{name}' run completed with warnings",
    RunAlertType.FAILED: "Batch pipeline '{name}' run encountered a failure",
    RunAlertType.UNEXPECTED_STATUS_CHANGE: "Batch pipeline '{name}' run status changed from end status",
}
"""Description templates for run alerts"""

INSTANCE_ALERT_DESCRIPTIONS: dict[InstanceAlertType, str] = {
    InstanceAlertType.DATASET_NOT_READY: "{component_name} asset did not arrive when expected",
    InstanceAlertType.INCOMPLETE: "Instance ended; component progress incomplete",
    InstanceAlertType.OUT_OF_SEQUENCE: "Journey executed out-of-sequence",
    InstanceAlertType.TESTS_FAILED: "{component_type} ‘{component_name}’ tests failed",
    InstanceAlertType.TESTS_HAD_WARNINGS: "{component_type} ‘{component_name}’ tests have warnings",
}
