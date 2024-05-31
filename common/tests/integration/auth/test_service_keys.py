import pytest

from common.auth.keys import service_key
from common.entities import Company, Organization, Project, Service


@pytest.fixture
def project():
    c = Company.create(name="DataKitchen")
    o = Organization.create(name="DK Orange Peels", company=c)
    project = Project.create(name="DK Remote", organization=o)
    yield project


@pytest.mark.integration
def test_generate_and_validate_key(project):
    new_key = service_key.generate_key(allowed_services=[Service.EVENTS_API.name], project=project).encoded_key
    data = service_key.validate_key(new_key)
    assert data.valid is True
    assert data.allowed_services == [Service.EVENTS_API.name]
