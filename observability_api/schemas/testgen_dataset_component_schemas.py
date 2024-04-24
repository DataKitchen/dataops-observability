__all__ = ["TestgenDatasetComponentSchema"]

from marshmallow.fields import List, Str

from common.entities import TestgenDatasetComponent
from observability_api.schemas.base_schemas import BaseEntitySchema


class TestgenDatasetComponentSchema(BaseEntitySchema):
    table_list = List(Str())
    integration_name = Str(dump_only=True, dump_default="TESTGEN")

    class Meta:
        model = TestgenDatasetComponent
