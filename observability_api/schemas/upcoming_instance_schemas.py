__all__ = ["UpcomingInstanceSchema"]


from marshmallow import Schema
from marshmallow.fields import DateTime, Nested, Pluck

from observability_api.schemas.journey_schemas import JourneyProjectSchema, JourneySchema


# This schema is only used for dumping
class UpcomingInstanceSchema(Schema):
    project = Pluck(JourneyProjectSchema, "project", attribute="journey", dump_only=True)
    journey = Nested(JourneySchema(only=["id", "name"]))
    expected_start_time = DateTime(
        metadata={"description": "The upcoming instance's expected start time"},
    )
    expected_end_time = DateTime(
        metadata={"description": "The upcoming instance's expected end time"},
    )
