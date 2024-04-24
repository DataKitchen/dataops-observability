from itertools import count
from unittest.mock import patch

import pytest

from common.kubernetes import readiness_probe


class SentinelException(Exception):
    pass


@pytest.fixture
def set_ready_mock():
    with patch.object(readiness_probe, "set_ready") as mock:
        yield mock


@pytest.mark.unit
@patch.object(readiness_probe.tempfile, "gettempdir", return_value="/xpto")
def test_get_filename(temp_dir_mock):
    assert readiness_probe._get_mark_file_path() == "/xpto/observability_readyz"
    temp_dir_mock.assert_called_once()


@pytest.mark.unit
def test_wrapper_mark_ready(set_ready_mock):
    with readiness_probe.readiness_check_wrapper():
        pass
    set_ready_mock.assert_called_once()


@pytest.mark.unit
def test_wrapper_not_mark_ready(set_ready_mock):
    with pytest.raises(SentinelException):
        with readiness_probe.readiness_check_wrapper():
            raise SentinelException("Nop")
    set_ready_mock.assert_not_called()


@pytest.mark.unit
@patch.object(readiness_probe, "is_ready", return_value=True)
@patch.object(readiness_probe.sys, "exit", side_effect=SentinelException("exit_called"))
def test_wait_ready(exit_mock, is_ready_mock):
    with pytest.raises(SentinelException):
        readiness_probe.block_until_ready_and_exit(20)
    is_ready_mock.assert_called_once()
    exit_mock.assert_called_once_with()


@pytest.mark.unit
@patch.object(readiness_probe, "is_ready", return_value=False)
@patch.object(readiness_probe.time, "sleep")
@patch.object(readiness_probe.time, "time", side_effect=count())
@patch.object(readiness_probe.sys, "exit", side_effect=SentinelException("exit_called"))
def test_wait_not_ready(exit_mock, _, sleep_mock, is_ready_mock):
    with pytest.raises(SentinelException):
        readiness_probe.block_until_ready_and_exit(3)
    assert is_ready_mock.call_count == 2
    assert sleep_mock.call_count == 2
    exit_mock.assert_called_once_with(1)
