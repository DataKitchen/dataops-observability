import logging
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional, Type

from flask import Response, current_app, g, make_response, request
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from common.api.base_view import PERM_PROJECT, BaseView
from common.events.enums import EventSources
from common.events.v1 import Event
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS, KafkaProducer, MessageError, MessageTooLargeError, ProducerError

LOG = logging.getLogger(__name__)


class EventView(BaseView):
    """
    Base view for an Event.

    To add new event-type to the API:

    1. Create a new Event dataclass, following the instructions in common/events/ARCHITECTURE.md
    2. Create an EventView subclass in event_api/endpoints/v#/
    3. Set event_type to your new event dataclass.
    4. Add your endpoint to event_api/routes/v#_routes.py
    5. Add a doc-string to the endpoint. Note: See generate_api_spec.py. There is a bug in ApiSpec that causes
       components to be wrongly referenced. As a workaround, reference Schema-name + RequestBody. e.g.,
       myschema -> myschemaRequestBody.
    """

    PERMISSION_REQUIREMENTS = (PERM_PROJECT,)
    event_type: Type[Event]
    """The class (not instance) that is used to deserialize the incoming request body"""

    def make_error(self, msg: str, e: Exception, error_code: Optional[int] = None) -> Response:
        """TODO: This should be turned into an ErrorHandler at the app level."""
        return make_response(
            {
                "error": msg,
                # TODO: Should this be exposed to the user?
                "details": str(e),
                "timestamp": datetime.now(tz=timezone.utc),
            },
            error_code if error_code else 500,
        )

    def post(self) -> Response:
        if request.content_length > current_app.config["MAX_REQUEST_BODY_SIZE"]:
            raise RequestEntityTooLarge("Request Entity Too Large")

        try:
            event: Event = self.event_type.as_event_from_request(self.request_body)
        except ValidationError as ve:
            raise BadRequest(f"Invalid request: {str(ve)}") from ve
        try:
            source = EventSources(request.headers.get("EVENT-SOURCE", EventSources.API.name).upper())
            event.source = source.value
        except ValueError:
            raise BadRequest(f"Invalid EVENT-SOURCE. Valid EVENT-SOURCE: {', '.join(e.value for e in EventSources)}.")

        # g.project should be set by the ServiceAccountAuth extension or other authentication methods.
        event.project_id = g.project.id
        try:
            with KafkaProducer({}) as producer:
                producer.produce(TOPIC_UNIDENTIFIED_EVENTS, event)
        except MessageTooLargeError:
            LOG.warning(
                "Attempt to send a large '%s' event",
                request.path,
                extra={"request_size": request.content_length, "message_size": len(event.as_bytes())},
            )
            raise RequestEntityTooLarge("Request Entity Too Large")
        except (MessageError, ProducerError) as e:
            LOG.exception("Error producing '%s' event", request.path)
            return self.make_error("An error has occurred; event could not be processed", e)

        LOG.debug("%s: Event Posted from '%s'", request.path, event.source)
        return make_response({}, HTTPStatus.NO_CONTENT)
