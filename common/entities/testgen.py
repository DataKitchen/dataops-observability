__all__ = ["TestgenDatasetComponent", "TestGenTestOutcomeIntegration"]

from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, UUIDField

from ..peewee_extensions.fields import JSONDictListField, JSONStrListField
from .base_entity import BaseEntity
from .component import Component
from .test_outcome import TestOutcome


class TestgenDatasetComponent(BaseEntity):
    database_name = CharField(null=False)
    connection_name = CharField(null=False)
    schema = CharField(null=True)
    table_list = JSONStrListField(null=False)
    table_include_pattern = CharField(null=True)
    table_exclude_pattern = CharField(null=True)
    table_group_id = UUIDField(null=True)
    project_code = CharField(null=True)
    uses_sampling = BooleanField(default=False, null=True)
    sample_percentage = CharField(null=True)
    sample_minimum_count = IntegerField(null=True)
    component = ForeignKeyField(Component, backref="testgen_components", on_delete="CASCADE", null=False, unique=True)

    class Meta:
        table_name = "testgen_dataset_component"


class TestGenTestOutcomeIntegration(BaseEntity):
    table = CharField(null=False)
    columns = JSONStrListField(null=True)
    test_suite = CharField(null=False)
    version = IntegerField(null=False)
    test_outcome = ForeignKeyField(
        TestOutcome, null=False, backref="testgen_test_outcome_integrations", on_delete="CASCADE"
    )
    test_parameters = JSONDictListField(null=False)

    class Meta:
        table_name = "test_outcome_integration"
