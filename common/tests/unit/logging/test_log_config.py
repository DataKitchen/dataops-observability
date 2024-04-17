import json
from logging import Logger
from unittest.mock import MagicMock

import pytest

from common.logging import JsonFormatter


@pytest.mark.unit
def test_json_log_formatter():
    """JsonFormatter formats log messages as line-item-json."""
    formatter = JsonFormatter()
    LOG = Logger("test-logger", 10)
    LOG.handle = MagicMock()
    LOG.info("An info message")
    LOG.handle.assert_called()

    # call_args first value is a tuple of positional arguments
    positional_args = LOG.handle.call_args[0]
    # the constructed record is the first of the positional arguments
    record = positional_args[0]

    msg = formatter.format(record)
    msg_dict = json.loads(msg)

    for key in ("timestamp", "message", "stackinfo", "traceback"):
        assert key in msg_dict


@pytest.mark.unit
def test_extra_kwargs_logging():
    """Extra keyword arguments given in a log message are included in JSON formatted log message."""
    formatter = JsonFormatter()
    LOG = Logger("test-logger", 10)
    LOG.handle = MagicMock()
    LOG.info("An info message", extra={"testkey": 1})
    LOG.handle.assert_called()

    # call_args first value is a tuple of positional arguments
    positional_args = LOG.handle.call_args[0]
    # the constructed record is the first of the positional arguments
    record = positional_args[0]

    msg = formatter.format(record)
    msg_dict = json.loads(msg)
    assert "testkey" in msg_dict


@pytest.mark.unit
def test_formatting_args():
    """Argument formatted messages are fully formatted before being dumped by the JsonFormatter."""
    formatter = JsonFormatter()
    LOG = Logger("test-logger", 10)
    LOG.handle = MagicMock()
    LOG.info("An info message arg: %s", "testarg")
    LOG.handle.assert_called()

    # call_args first value is a tuple of positional arguments
    positional_args = LOG.handle.call_args[0]
    # the constructed record is the first of the positional arguments
    record = positional_args[0]

    msg = formatter.format(record)
    msg_dict = json.loads(msg)

    assert msg_dict["message"] == "An info message arg: testarg"


@pytest.mark.unit
def test_traceback_json_log():
    """Traceback data is shipped along with JSON when present."""
    formatter = JsonFormatter()
    LOG = Logger("test-logger", 10)
    LOG.handle = MagicMock()
    try:
        int("cat")
    except ValueError:
        LOG.exception("Cats are not integers")

    LOG.handle.assert_called()

    # call_args first value is a tuple of positional arguments
    positional_args = LOG.handle.call_args[0]
    # the constructed record is the first of the positional arguments
    record = positional_args[0]

    msg = formatter.format(record)
    msg_dict = json.loads(msg)
    traceback = msg_dict.get("traceback", None)
    assert traceback, "Traceback should have been populated"
