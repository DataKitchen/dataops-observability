__all__ = [
    "JourneyDagEdgeCompactSchema",
    "JourneyDagEdgeSchema",
    "JourneyDagNodeSchema",
    "JourneyDagSchema",
    "JourneyDagEdgePostSchema",
]
from marshmallow import EXCLUDE, Schema
from marshmallow.fields import UUID, List, Nested, Pluck, Str

from .base_schemas import BaseEntitySchema
from .component_schemas import ComponentSchema
from .journey_schemas import JourneySchema


class JourneyDagEdgeSchema(BaseEntitySchema):
    journey = Pluck(JourneySchema, "id", required=True)
    left = Pluck(ComponentSchema, "id", required=False)
    right = Pluck(ComponentSchema, "id", required=True)

    class Meta:
        unknown = EXCLUDE


class JourneyDagEdgeCompactSchema(Schema):
    id = Str()
    left = Pluck(ComponentSchema, "id", required=False, data_key="component")


class JourneyDagEdgePostSchema(Schema):
    left = UUID(required=False)
    right = UUID(required=True)


class JourneyDagNodeSchema(Schema):
    component = Nested(ComponentSchema, required=True)
    edges = Nested(JourneyDagEdgeCompactSchema, required=True, many=True)

    class Meta:
        unknown = EXCLUDE


class JourneyDagSchema(Schema):
    nodes = List(Nested(JourneyDagNodeSchema), required=True)
