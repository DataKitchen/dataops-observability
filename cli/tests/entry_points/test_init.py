from collections import OrderedDict
from unittest.mock import patch

import pytest

from cli.entry_points.init import Initialize
from common.entities import ALL_MODELS, DB, Company, Organization, Project, User


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


@pytest.mark.integration
def test_init_user_supplied_data(init_entry_point, mock_user_input, user_data):
    with patch.dict(init_entry_point.kwargs, {"default": False}):
        init_entry_point.subcmd_entry_point()

    assert Company.select().count() == 1
    assert Organization.select().count() == 1
    assert Project.select().count() == 1
    assert User.select().count() == 1
    assert User.get().username == user_data["username"]


@pytest.mark.integration
def test_init_default_data(init_entry_point):
    init_entry_point.subcmd_entry_point()

    assert Company.select().count() == 1
    assert Organization.select().count() == 1
    assert Project.select().count() == 1
    assert User.select().count() == 1
    assert User.get().username == "default"


@pytest.mark.integration
def test_init_tables_exists(init_entry_point, create_tables_mock):
    DB.create_tables(ALL_MODELS)

    init_entry_point.subcmd_entry_point()

    create_tables_mock.assert_not_called()
    assert Company.select().count() == 1
    assert Organization.select().count() == 1
    assert Project.select().count() == 1
    assert User.select().count() == 1
    assert User.get().username == "default"


@pytest.mark.integration
def test_init_not_empty(init_entry_point, create_tables_mock):
    DB.create_tables(ALL_MODELS)
    Company.create(name="Existing")

    with patch.dict(init_entry_point.kwargs, {"force": True}):
        init_entry_point.subcmd_entry_point()

    create_tables_mock.assert_not_called()
    assert Company.select().count() == 1
    assert Organization.select().count() == 1
    assert Project.select().count() == 1
    assert User.select().count() == 1
    assert User.get().username == "default"


@pytest.mark.integration
def test_init_not_empty_abort(init_entry_point, create_tables_mock):
    DB.create_tables(ALL_MODELS)
    Company.create(name="Existing")
    Company.create(name="Existing2")

    with patch("cli.entry_points.init.sys.exit") as exit_mock:
        init_entry_point.subcmd_entry_point()

    exit_mock.assert_called_once_with(1)
    create_tables_mock.assert_not_called()
    assert Company.select().count() == 2
    assert Organization.select().count() == 0
    assert Project.select().count() == 0
    assert User.select().count() == 0


@pytest.mark.integration
def test_init_error(init_entry_point):
    DB.create_tables(ALL_MODELS)
    Organization.drop_table()

    with patch("cli.entry_points.init.sys.exit") as exit_mock:
        init_entry_point.subcmd_entry_point()

    exit_mock.assert_called_once_with(2)
    assert Company.select().count() == 0
