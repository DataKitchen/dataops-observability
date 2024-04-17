import pytest

from common.entities import RunTaskStatus


@pytest.mark.unit
def test_runtaskstatus_max():
    assert RunTaskStatus.max(RunTaskStatus.FAILED.name, RunTaskStatus.FAILED.name) == RunTaskStatus.FAILED
    assert (
        RunTaskStatus.max(RunTaskStatus.COMPLETED_WITH_WARNINGS.name, RunTaskStatus.COMPLETED_WITH_WARNINGS.name)
        == RunTaskStatus.COMPLETED_WITH_WARNINGS
    )
    assert RunTaskStatus.max(RunTaskStatus.COMPLETED.name, RunTaskStatus.COMPLETED.name) == RunTaskStatus.COMPLETED
    assert RunTaskStatus.max(RunTaskStatus.RUNNING.name, RunTaskStatus.RUNNING.name) == RunTaskStatus.RUNNING
    assert RunTaskStatus.max(RunTaskStatus.MISSING.name, RunTaskStatus.MISSING.name) == RunTaskStatus.MISSING
    assert RunTaskStatus.max(RunTaskStatus.PENDING.name, RunTaskStatus.PENDING.name) == RunTaskStatus.PENDING

    assert (
        RunTaskStatus.max(RunTaskStatus.FAILED.name, RunTaskStatus.COMPLETED_WITH_WARNINGS.name) == RunTaskStatus.FAILED
    )
    assert RunTaskStatus.max(RunTaskStatus.FAILED.name, RunTaskStatus.COMPLETED.name) == RunTaskStatus.FAILED
    assert RunTaskStatus.max(RunTaskStatus.FAILED.name, RunTaskStatus.RUNNING.name) == RunTaskStatus.FAILED
    assert RunTaskStatus.max(RunTaskStatus.FAILED.name, RunTaskStatus.MISSING.name) == RunTaskStatus.FAILED
    assert RunTaskStatus.max(RunTaskStatus.FAILED.name, RunTaskStatus.PENDING.name) == RunTaskStatus.FAILED

    assert (
        RunTaskStatus.max(RunTaskStatus.COMPLETED_WITH_WARNINGS.name, RunTaskStatus.COMPLETED.name)
        == RunTaskStatus.COMPLETED_WITH_WARNINGS
    )
    assert (
        RunTaskStatus.max(RunTaskStatus.COMPLETED_WITH_WARNINGS.name, RunTaskStatus.RUNNING.name)
        == RunTaskStatus.COMPLETED_WITH_WARNINGS
    )
    assert (
        RunTaskStatus.max(RunTaskStatus.COMPLETED_WITH_WARNINGS.name, RunTaskStatus.MISSING.name)
        == RunTaskStatus.COMPLETED_WITH_WARNINGS
    )
    assert (
        RunTaskStatus.max(RunTaskStatus.COMPLETED_WITH_WARNINGS.name, RunTaskStatus.PENDING.name)
        == RunTaskStatus.COMPLETED_WITH_WARNINGS
    )

    assert RunTaskStatus.max(RunTaskStatus.COMPLETED.name, RunTaskStatus.RUNNING.name) == RunTaskStatus.COMPLETED
    assert RunTaskStatus.max(RunTaskStatus.COMPLETED.name, RunTaskStatus.MISSING.name) == RunTaskStatus.COMPLETED
    assert RunTaskStatus.max(RunTaskStatus.COMPLETED.name, RunTaskStatus.PENDING.name) == RunTaskStatus.COMPLETED

    assert RunTaskStatus.max(RunTaskStatus.RUNNING.name, RunTaskStatus.MISSING.name) == RunTaskStatus.RUNNING
    assert RunTaskStatus.max(RunTaskStatus.RUNNING.name, RunTaskStatus.PENDING.name) == RunTaskStatus.RUNNING

    assert RunTaskStatus.max(RunTaskStatus.MISSING.name, RunTaskStatus.PENDING.name) == RunTaskStatus.MISSING

    with pytest.raises(ValueError):
        RunTaskStatus.max("invalid type", RunTaskStatus.PENDING.name)
