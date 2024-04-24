from http import HTTPStatus

import pytest

from common.entities import Company, Organization, Project


@pytest.mark.integration
def test_32_uuid_converter(client, g_user_2_admin):
    # We have a converter which allows us to reference UUIDs by their dashless version
    company = Company.create(name="Foo")
    org = Organization.create(name="Foo", company=company)
    proj = Project.create(name="Foo", active=True, organization=org)
    response = client.get(f"/observability/v1/projects/{str(proj.id).replace('-', '')}")
    assert response.status_code == HTTPStatus.OK, response.json
    assert response.json["id"] == str(proj.id)
