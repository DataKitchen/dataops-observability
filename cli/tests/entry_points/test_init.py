import io
import json
from collections import OrderedDict
from unittest.mock import patch

import pytest

from cli.entry_points.init import Initialize
from common.entities import ALL_MODELS, DB, Action, Company, Organization, Project, ServiceAccountKey, User


@pytest.fixture
def create_tables_mock():
    with patch("cli.entry_points.init.create_all_tables") as create_tables_mock:
        create_tables_mock.side_effect = lambda db, **_: db.create_tables(ALL_MODELS)
        yield create_tables_mock


@pytest.fixture
def init_entry_point(test_db, create_tables_mock):
    yield Initialize(default=True)


@pytest.fixture
def user_data():
    return OrderedDict(
        (
            ("name", "Joe"),
            ("email", "joe@example.com"),
            ("username", "joeuser"),
            ("password", "easy"),
        )
    )


@pytest.fixture
def mock_user_input(user_data):
    with patch("cli.entry_points.init.input", side_effect=user_data.values()) as input_mock:
        yield input_mock


@pytest.fixture
def mock_user_input_json(user_data):
    with patch("cli.entry_points.init.input", return_value=json.dumps(user_data)) as input_mock:
        yield input_mock


@pytest.mark.integration
@pytest.mark.parametrize(
    ("has_tables", "has_data", "args"),
    (
        (False, False, {}),
        (False, False, {"tables": True, "force": True}),
        (True, False, {"tables": True}),
        (True, True, {"data": True}),
        (True, True, {"demo": True}),
    ),
    ids=(
        "no args",
        "--force' used with --tables",
        "--tables with existing tables",
        "--data with existing data and no --force",
        "--demo with existing data and no --force",
    ),
)
def test_init_abort_invalid_args(has_tables, has_data, args, init_entry_point, create_tables_mock):
    if has_tables:
        DB.create_tables(ALL_MODELS)

    if has_data:
        Company.create(name="Existing")

    with (
        patch("cli.entry_points.init.sys.exit") as exit_mock,
        patch.dict(init_entry_point.kwargs, args, clear=True),
    ):
        init_entry_point.subcmd_entry_point()

    create_tables_mock.assert_not_called()
    exit_mock.assert_called_once_with(1)


@pytest.mark.integration
def test_init_json(init_entry_point, mock_user_input_json, user_data, capsys):
    with (
        patch.dict(init_entry_point.kwargs, {"demo": True, "json": True}),
    ):
        init_entry_point.subcmd_entry_point()

    assert Company.select().count() == 1
    assert Organization.select().count() == 1
    assert Project.select().count() == 1
    assert User.select().count() == 1
    assert User.get().username == user_data["username"]
    assert Action.select().count() == 1
    assert ServiceAccountKey.select().count() == 1

    output = json.loads(capsys.readouterr().out)
    assert "company_id" in output, output
    assert "organization_id" in output, output
    assert "project_id" in output, output
    assert "user_id" in output, output
    assert "action_id" in output, output
    assert "service_account_key" in output, output


@pytest.mark.integration
@pytest.mark.parametrize("arg", ("demo", "data"))
def test_init_not_empty(arg, init_entry_point, create_tables_mock, mock_user_input):
    DB.create_tables(ALL_MODELS)
    Company.create(name="Existing")

    with patch.dict(init_entry_point.kwargs, {arg: True, "force": True}):
        init_entry_point.subcmd_entry_point()

    create_tables_mock.assert_not_called()
    assert Company.select().count() == 1
    assert Organization.select().count() == 1
    assert Project.select().count() == 1
    assert User.select().count() == 1
    assert User.get().username == "joeuser"

    demo_data_count = 1 if arg == "demo" else 0
    assert Action.select().count() == demo_data_count
    assert ServiceAccountKey.select().count() == demo_data_count


@pytest.mark.integration
def test_init_error(init_entry_point, mock_user_input):
    DB.create_tables(ALL_MODELS)
    Organization.drop_table()

    with (
        patch("cli.entry_points.init.sys.exit") as exit_mock,
        patch.dict(init_entry_point.kwargs, {"data": True}),
    ):
        init_entry_point.subcmd_entry_point()

    exit_mock.assert_called_once_with(2)
    assert Company.select().count() == 0
