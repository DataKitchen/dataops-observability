import sys
from unittest.mock import Mock, patch

import pytest

from common import argparse


@pytest.fixture
def handler():
    def handler_func(_):
        yield

    handler_mock = Mock()
    handler_mock.side_effect = handler_func(None)
    yield handler_mock


@pytest.fixture
def mod():
    with patch.object(argparse, "REGISTERED_HANDLERS", []):
        yield argparse


@pytest.mark.unit
@pytest.mark.parametrize("count", [1, 3])
def test_handler_registered(mod, count, handler):
    for _ in range(count):
        mod.add_arg_handler(handler)
    assert handler in argparse.REGISTERED_HANDLERS
    assert len(argparse.REGISTERED_HANDLERS) == 1
    handler.assert_not_called()


@pytest.mark.unit
@patch.object(sys, "argv", ["xpto", "--some-arg"])
def test_handler_called_with_args(mod):
    handling_mock = Mock()

    def handler(parser):
        parser.add_argument("--some-arg", action="store_true")
        args = yield
        handling_mock(args.some_arg)

    mod.add_arg_handler(handler)
    mod.handle_args()

    handling_mock.assert_called_once_with(True)
