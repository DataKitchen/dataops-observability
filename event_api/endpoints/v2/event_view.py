import logging
from http import HTTPStatus
from typing import Type

from flask import Response, g, make_response
from marshmallow import Schema, ValidationError
from werkzeug.exceptions import BadRequest, InternalServerError

from common.api.base_view import PERM_PROJECT, BaseView
from common.events.v2 import EventResponseSchema, EventV2
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS, KafkaProducer, MessageError, ProducerError

LOG = logging.getLogger(__name__)


class BaseEventView(BaseView):
    PERMISSION_REQUIREMENTS = (PERM_PROJECT,)
    payload_schema: Schema = NotImplemented
    event_type: Type[EventV2]

    def post(self) -> Response:
        try:
            event_payload = self.parse_body(schema=self.payload_schema)
        except ValidationError:
            raise BadRequest()

        event = self.event_type(
            event_payload=event_payload,
            project_id=g.project.id,
        )

        try:
            with KafkaProducer({}) as producer:
                producer.produce(TOPIC_UNIDENTIFIED_EVENTS, event)
        except (MessageError, ProducerError) as e:
            LOG.exception(str(e))
            raise InternalServerError()

        return make_response(EventResponseSchema().dump(event), HTTPStatus.ACCEPTED)
