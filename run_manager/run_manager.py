import logging
import time
from collections import namedtuple
from dataclasses import asdict
from itertools import chain
from typing import Union
from collections.abc import Callable

from peewee import DatabaseError, InterfaceError, OperationalError

from common.entities import DB
from common.events import to_v2
from common.events.internal import ScheduledEvent, ScheduledInstance
from common.events.v1 import Event
from common.kafka import (
    TOPIC_DEAD_LETTER_OFFICE,
    TOPIC_IDENTIFIED_EVENTS,
    TOPIC_SCHEDULED_EVENTS,
    TOPIC_UNIDENTIFIED_EVENTS,
    ConsumerError,
    KafkaTransactionalConsumer,
    KafkaTransactionalProducer,
    MessageError,
    ProducerError,
    ProducerTransactionError,
)
from common.kubernetes.readiness_probe import NotReadyException, readiness_check_wrapper
from conf import init_db
from run_manager.context import RunManagerContext
from run_manager.event_handlers import (
    DatasetHandler,
    IncompleteInstanceHandler,
    InstanceHandler,
    RunHandler,
    TaskHandler,
    TestOutcomeHandler,
    handle_schedule_event,
)
from run_manager.event_handlers.component_identifier import ComponentIdentifier
from run_manager.event_handlers.out_of_sequence_instance_handler import OutOfSequenceInstanceHandler
from run_manager.event_handlers.run_unexpected_status_change_handler import RunUnexpectedStatusChangeHandler
from run_manager.event_handlers.scheduled_instance_handler import handle_scheduled_instance_event

LOG = logging.getLogger(__name__)

EventHandlingResult = namedtuple("EventHandlingResult", ("success", "alerts"))


class RunManager:
    def __init__(
        self,
        event_consumer: KafkaTransactionalConsumer,
        event_producer: KafkaTransactionalProducer,
    ) -> None:
        self.event_consumer = event_consumer
        self.event_producer = event_producer

    def _handle_event(self, event: Event) -> EventHandlingResult:
        context = RunManagerContext()
        event.accept(ComponentIdentifier(context))
        # If no component (including pipeline) was found, it means something is wrong with the event, and
        # it needs to go to the dead letter office
        if not context.component or not event.component_key_details:
            LOG.warning(f"No component was found for event. {event}")
            self.event_producer.produce(TOPIC_DEAD_LETTER_OFFICE, event)
            return EventHandlingResult(False, [])
        event.component_id = context.component.id

        run_handler = RunHandler(context)
        event.accept(run_handler)
        event.run_id = context.run.id if context.run else None

        event.accept(InstanceHandler(context))
        event.instances = context.instances

        # Run and Instances relationship must be established before run alert is checked
        run_status_change_handler = RunUnexpectedStatusChangeHandler(context)
        event.accept(run_status_change_handler)

        event.accept(TaskHandler(context))
        event.task_id = context.task.id if context.task else None
        event.run_task_id = context.run_task.id if context.run_task else None

        test_outcome_handler = TestOutcomeHandler(context)
        event.accept(test_outcome_handler)
        event.accept(DatasetHandler(context))
        incomplete_handler = IncompleteInstanceHandler(context)
        incomplete_handler.check()
        out_of_sequence_instance_handler = OutOfSequenceInstanceHandler(context)
        event.accept(out_of_sequence_instance_handler)
        return EventHandlingResult(
            True,
            chain(
                test_outcome_handler.alerts,
                run_status_change_handler.alerts,
                incomplete_handler.alerts,
                out_of_sequence_instance_handler.alerts,
            ),
        )

    def _manage_user_event(self, event: Event) -> None:
        start = time.time()
        delay = start - event.received_timestamp.timestamp()
        result = self._handle_event(event)
        if result.success:
            to_v2(event).to_event_entity().save(force_insert=True)
            self.event_producer.produce(TOPIC_IDENTIFIED_EVENTS, event)
        for alert in result.alerts:
            self.event_producer.produce(TOPIC_IDENTIFIED_EVENTS, alert)
        elapsed = time.time() - start
        LOG.info("%s received %.2f seconds ago processed within %.2f seconds", type(event).__name__, delay, elapsed)

    def _manage_schedule_event(self, event: Union[ScheduledEvent, ScheduledInstance]) -> None:
        alerts = []
        if isinstance(event, ScheduledEvent):
            events = handle_schedule_event(event)
            for run_event in events.run_statuses:
                for alert in self._handle_event(run_event).alerts:
                    self.event_producer.produce(TOPIC_IDENTIFIED_EVENTS, alert)
            alerts = events.alerts
        elif isinstance(event, ScheduledInstance):
            ended_instances = handle_scheduled_instance_event(event)
            incomplete_handler = IncompleteInstanceHandler(RunManagerContext(ended_instances=ended_instances))
            incomplete_handler.check()
            alerts = incomplete_handler.alerts

        for alert in alerts:
            self.event_producer.produce(TOPIC_IDENTIFIED_EVENTS, alert)

    def process_events(self) -> None:
        with readiness_check_wrapper():
            init_db()
            self.event_consumer.connect()
            self.event_producer.connect()

            if not self.event_producer.is_topic_available(TOPIC_IDENTIFIED_EVENTS):
                raise NotReadyException(f"Kafka topic not ready: {TOPIC_IDENTIFIED_EVENTS.name}")
        try:
            with self.event_producer:
                managers: dict[str, Callable] = {
                    TOPIC_UNIDENTIFIED_EVENTS.name: self._manage_user_event,
                    TOPIC_SCHEDULED_EVENTS.name: self._manage_schedule_event,
                }
                for message in self.event_consumer:
                    try:
                        # As long as we don't terminate on errors we need to
                        # establish the database connection on each consumed
                        # message to counter stale database connections. When
                        # we terminate on errors the solution could be to
                        # reconnect at restart which should yield the least
                        # overhead as checking for stale connection requires
                        # pinging the server.
                        init_db()
                        with self.event_producer.transaction(), DB.atomic():
                            # This large DB transaction is trying to match the
                            # Kafka transaction. If the DB transaction fails the
                            # Kafka transaction will not be committed. It is still
                            # possible that the Kafka transaction fails after the
                            # DB transaction was committed though.
                            managers[message.topic](message.payload)
                    except ProducerTransactionError:
                        # if the error came from the transactional producer, let the process restart
                        # this error's base ProducerError is caught and logged below
                        raise
                    except (InterfaceError, OperationalError) as e:
                        # OperationalError has been seen during migrations such as adding table indexes. Catching
                        # and reraising the exception to re-consume the event. InterfaceError is related to the
                        # connection and should benefit from re-consuming too.
                        LOG.error("Database error occured: %s", e)
                        raise
                    except Exception:
                        LOG.exception(
                            "Error processing an event, continuing...",
                            extra={"kafka_message": asdict(message)},
                        )
                        self.event_consumer.commit()
                    finally:
                        try:
                            DB.close()
                        except Exception:
                            pass  # It probably wasn't open
        except (ConsumerError, MessageError, ProducerError, DatabaseError, InterfaceError):
            LOG.exception("Error processing events, stopping...")
