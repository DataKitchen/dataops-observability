from pathlib import Path

import pytest

from common.entities import Company, Organization, Project, ServiceAccountKey
from common.peewee_extensions import fixtures

FIXTURE_DIR = Path(__file__).resolve().parent.joinpath("fixtures")
BAD_FIXTURE_DIR = FIXTURE_DIR.parent.joinpath("bad_fixtures")


@pytest.mark.unit
def test_read_fixture_file():
    company_toml = FIXTURE_DIR.joinpath("company.toml")
    result = fixtures.read_file(company_toml)
    assert result.get("table_name") == "company"
    assert result.get("fixture_id") == "9da3a73e-ac41-4ef3-9527-0bee2cb1232d"
    assert result.get("requires_id") is None
    assert len(result.get("row")) == 1, f"Expected only 1 row in the company fixture, got {len(result.get('row'))}"


@pytest.mark.unit
def test_read_fixture_folder():
    results = fixtures.read_folder(FIXTURE_DIR)
    for result in results:
        table = result.get("table_name")
        if table == "company":
            assert result.get("fixture_id") == "9da3a73e-ac41-4ef3-9527-0bee2cb1232d"
        elif table == "organization":
            assert result.get("fixture_id") == "7030ed67-1fdd-4d7e-8ca0-f758599600b6"
            assert result.get("requires_id") == "9da3a73e-ac41-4ef3-9527-0bee2cb1232d"
        elif table == "project":
            assert result.get("fixture_id") == "70fe8951-d433-426d-8c08-5ca96117f740"
            assert result.get("requires_id") == "7030ed67-1fdd-4d7e-8ca0-f758599600b6"
        elif table == "service_account_key":
            assert result.get("fixture_id") == "bed70422-32de-40f4-a781-555e4238e11d"
            assert result.get("requires_id") == "70fe8951-d433-426d-8c08-5ca96117f740"
        else:
            raise AssertionError(f"Unexpected table name in fixture data: {table}")
        assert len(result.get("row")) == 1, f"Expected only 1 row in {table} fixture, got {len(result.get('row'))}"


@pytest.mark.integration
def test_load_company_fixture_file(test_db):
    company_toml = FIXTURE_DIR.joinpath("company.toml")
    fixtures.load_file(company_toml)
    total = Company.select().count()
    assert total == 1, f"Expected 1 Company in the DB, found {total}"


@pytest.mark.integration
def test_load_fixture_folder(test_db):
    fixtures.load_folder(FIXTURE_DIR)
    for model_class in (Company, Organization, Project, ServiceAccountKey):
        count = model_class.select().count()
        assert count == 1, f"Expected 1 {model_class.__name__} in the DB, found: {count}"


@pytest.mark.integration
def test_load_fixture_folder_bad(test_db):
    # The files in the bad_fixtures folder don't have a valid dependency graph and so should raise an error
    with pytest.raises(ValueError):
        fixtures.load_folder(BAD_FIXTURE_DIR)
