__all__ = ["ComponentSchema", "ComponentPatchSchema"]

from marshmallow.fields import Dict, List, Nested, Pluck, Str
from marshmallow.validate import Regexp

from common.constants import (
    EXTENDED_ALPHANUMERIC_REGEX,
    INVALID_TOOL_VALUE,
    MAX_COMPONENT_TOOL_LENGTH,
    MAX_PIPELINE_KEY_LENGTH,
    MAX_SUBCOMPONENT_KEY_LENGTH,
)
from common.entities.component import Component, ComponentType
from common.schemas.fields import EnumStr, NormalizedStr, strip_upper_underscore
from common.schemas.validators import not_empty
from observability_api.schemas.base_schemas import AuditEntitySchemaMixin, BaseEntitySchema
from observability_api.schemas.project_schemas import ProjectSchema
from observability_api.schemas.testgen_dataset_component_schemas import TestgenDatasetComponentSchema


class ComponentSchema(BaseEntitySchema, AuditEntitySchemaMixin):
    project = Pluck(ProjectSchema, "id", dump_only=True)
    testgen_components = List(Nested(TestgenDatasetComponentSchema()), dump_only=True, data_key="integrations")
    labels = Dict(required=False)
    key = Str(validate=not_empty(max=MAX_PIPELINE_KEY_LENGTH))
    name = Str(required=False)
    display_name = Str(dump_only=True)
    type = EnumStr(required=True, enum=ComponentType)
    tool = NormalizedStr(
        required=False,
        load_default=None,
        normalizer=strip_upper_underscore,
        validate=[
            Regexp(EXTENDED_ALPHANUMERIC_REGEX, error=INVALID_TOOL_VALUE),
            not_empty(max=MAX_COMPONENT_TOOL_LENGTH),
        ],
    )

    class Meta:
        model = Component


class ComponentPatchSchema(BaseEntitySchema):
    key = Str(required=False, validate=not_empty(max=MAX_SUBCOMPONENT_KEY_LENGTH))
    name = Str(required=False, allow_none=True)
    description = Str(required=False, allow_none=True)
    labels = Dict(required=False)
    tool = NormalizedStr(
        required=False,
        allow_none=True,
        normalizer=strip_upper_underscore,
        validate=[
            Regexp(EXTENDED_ALPHANUMERIC_REGEX, error=INVALID_TOOL_VALUE),
            not_empty(max=MAX_COMPONENT_TOOL_LENGTH),
        ],
    )
