import pytest

from common.entities import Company, Organization
from common.tests.integration.entities.conftest import AuditUpdateTimeEntityClass


@pytest.mark.integration
def test_base_entity_save_new():
    company = Company.create(name="Foo")
    org = Organization(
        name="foo",
        company=company,
    )
    result = org.save(force_insert=True)
    assert result == 1
    assert org.id is not None
    assert org.created_on is not None


@pytest.mark.integration
def test_update_entity_with_update(audit_update_obj):
    """`updated_on` field should be set to the latest timestamp automatically on update"""
    (
        AuditUpdateTimeEntityClass.update({AuditUpdateTimeEntityClass.name: "B"})
        .where(AuditUpdateTimeEntityClass.id == audit_update_obj.id)
        .execute()
    )
    audit_update_obj2 = AuditUpdateTimeEntityClass.get()
    assert audit_update_obj.id == audit_update_obj2.id
    assert audit_update_obj2.name == "B"
    assert audit_update_obj2.updated_on > audit_update_obj.updated_on


@pytest.mark.integration
def test_update_entity_with_save(audit_update_obj):
    """`updated_on` field should be set to the latest timestamp automatically on update"""
    audit_update_obj.name = "B"
    audit_update_obj.save()
    audit_update_obj2 = AuditUpdateTimeEntityClass.get()
    assert audit_update_obj.id == audit_update_obj2.id
    assert audit_update_obj2.name == "B"
    assert audit_update_obj2.updated_on > audit_update_obj.updated_on
