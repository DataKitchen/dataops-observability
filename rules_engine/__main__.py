import logging
from logging.config import dictConfig
from typing import Union

from common import argparse
from common.kafka import TOPIC_IDENTIFIED_EVENTS, KafkaConsumer
from common.kubernetes import readiness_probe
from common.logging import JsonFormatter
from rules_engine.engine import RulesEngine


def init_logging(*, handler: str = "json") -> None:
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
            "common": {"handlers": [handler], "level": "INFO", "propagate": False},
            "rules_engine": {"handlers": [handler], "level": "INFO", "propagate": False},
        },
        "root": {"handlers": [handler]},
    }
    dictConfig(LOG_CONFIG)


LOG = logging.getLogger(__name__)

kafka_consumer_config: dict[str, Union[str, bool]] = {
    "group.id": "rules-engine-consumer",
    "auto.offset.reset": "earliest",
    "allow.auto.create.topics": True,
}


def main() -> None:
    init_logging()
    argparse.add_arg_handler(readiness_probe.get_args_handler(60))
    argparse.handle_args()
    LOG.info("Starting Rules Engine...")
    event_consumer = KafkaConsumer(kafka_consumer_config, [TOPIC_IDENTIFIED_EVENTS])
    rules_engine = RulesEngine(event_consumer=event_consumer)

    try:
        rules_engine.process_events()
    except Exception:
        LOG.exception("Unexpected error occurred, exiting...")
    finally:
        event_consumer.disconnect()

    LOG.info("Exiting...")


if __name__ == "__main__":
    main()
