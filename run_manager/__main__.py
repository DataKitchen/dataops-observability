import logging
from logging.config import dictConfig

from common import argparse
from common.kafka import (
    TOPIC_SCHEDULED_EVENTS,
    TOPIC_UNIDENTIFIED_EVENTS,
    KafkaTransactionalConsumer,
    KafkaTransactionalProducer,
)
from common.kubernetes import readiness_probe
from common.logging import JsonFormatter
from run_manager.run_manager import RunManager

LOG_CONFIG: dict[str, object] = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "JsonFormatter": {"()": JsonFormatter},
        "simple": {"format": "[%(levelname)s] %(message)s  [%(name)s:%(lineno)s]"},
    },
    "handlers": {
        "json": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "JsonFormatter",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "app": {"handlers": ["json"], "level": "INFO", "propagate": False},
        "app.logger": {"handlers": ["json"], "level": "INFO", "propagate": False},
        "common": {"handlers": ["json"], "level": "INFO", "propagate": False},
        "run_manager": {"handlers": ["json"], "level": "INFO", "propagate": False},
        "urllib3": {"handlers": ["json"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["json"]},
}
dictConfig(LOG_CONFIG)
LOG = logging.getLogger(__name__)

kafka_consumer_config = {
    "group.id": "run-manager-consumer",
    "auto.offset.reset": "earliest",
    "allow.auto.create.topics": True,
}


def main() -> None:
    argparse.add_arg_handler(readiness_probe.get_args_handler(60))
    argparse.handle_args()
    LOG.info("Starting Run Manager...")
    event_consumer = KafkaTransactionalConsumer(
        kafka_consumer_config,
        [TOPIC_UNIDENTIFIED_EVENTS, TOPIC_SCHEDULED_EVENTS],
    )
    event_producer = KafkaTransactionalProducer(config={}, tx_consumer=event_consumer)
    manager = RunManager(event_consumer, event_producer)
    try:
        manager.process_events()
    except Exception:
        LOG.exception("Unexpected error occurred, exiting...")
    finally:
        event_consumer.disconnect()
        event_producer.disconnect()
    LOG.info("Exiting...")
