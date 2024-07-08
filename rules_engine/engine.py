import logging
from dataclasses import asdict
from time import time

from peewee import InterfaceError, OperationalError, PeeweeException

from common.entities import DB
from common.events.internal import InstanceAlert, RunAlert
from common.events.v1 import Event
from common.kafka import ConsumerError, KafkaConsumer, MessageError
from common.kubernetes import readiness_check_wrapper
from conf import init_db

from .lib import process_instance_alert, process_run_alert, process_v1_event, process_project_alert
from .typing import PROJECT_EVENT

LOG = logging.getLogger(__name__)


class RulesEngine:
    def __init__(self, *, event_consumer: KafkaConsumer) -> None:
        self.event_consumer = event_consumer
        self.last_refresh = time()

    def process_events(self) -> None:
        with readiness_check_wrapper():
            self.event_consumer.connect()
            init_db()
        try:
            for message in self.event_consumer:
                try:
                    init_db()
                    event = message.payload
                    match event:
                        case InstanceAlert():
                            process_instance_alert(event)
                        case RunAlert():
                            process_run_alert(event)
                        case Event():
                            process_v1_event(event)
                        case PROJECT_EVENT():
                            process_project_alert(event)
                        case _:
                            LOG.info("Message payload %s is not a type supported by the rules engine.", type(event))
                except (InterfaceError, OperationalError) as e:
                    # OperationalError has been seen during migrations such as adding table indexes. Catching
                    # and reraising the exception to re-consume the event. InterfaceError is related to the
                    # connection and should benefit from re-consuming too.
                    LOG.error("Database error occured: %s", e)
                    raise
                except Exception:
                    LOG.exception("Error evaluating event", extra={"kafka_message": asdict(message)})
                    self.event_consumer.commit()
                    continue
                finally:
                    try:
                        DB.close()
                    # for how these exceptions were inferred; see peewee.py:3185
                    except InterfaceError:
                        LOG.warning("Attempted to close an uninitialized (or deferred) database connection.")
                    except OperationalError:
                        LOG.warning("Attempted to close a database connection while a transaction is open.")
                    except (PeeweeException, Exception):
                        LOG.exception("Unknown exception occurred while attempting to close the database.")
        except (ConsumerError, MessageError):
            LOG.exception("Error evaluating rules, stopping...")
