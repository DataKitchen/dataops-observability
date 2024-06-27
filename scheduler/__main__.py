import logging
import signal
import zoneinfo
from logging.config import dictConfig

from apscheduler.schedulers.blocking import BlockingScheduler

from common import argparse
from common.kafka import KafkaProducer
from common.kubernetes import readiness_check_wrapper, readiness_probe
from common.logging import JsonFormatter
from conf import init_db
from scheduler.agent_status import AgentStatusScheduleSource
from scheduler.component_expectations import ComponentScheduleSource
from scheduler.instance_expectations import InstanceScheduleSource


def init_logging(*, handler: str = "json") -> None:
    log_config: dict[str, object] = {
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
            "scheduler": {"handlers": [handler], "level": "INFO", "propagate": False},
            "apscheduler": {"handlers": [handler], "level": "INFO", "propagate": False},
        },
        "root": {"handlers": [handler]},
    }
    dictConfig(log_config)


LOG = logging.getLogger(__name__)


def main() -> None:
    init_logging()
    LOG.info("Starting Scheduler...")

    with readiness_check_wrapper():
        init_db()
        event_producer = KafkaProducer(config={})
        event_producer.connect()

    argparse.add_arg_handler(readiness_probe.get_args_handler(60))
    argparse.handle_args()

    scheduler = BlockingScheduler(job_defaults={"timezone": zoneinfo.ZoneInfo("UTC")})
    ComponentScheduleSource(scheduler, event_producer)
    InstanceScheduleSource(scheduler, event_producer)
    AgentStatusScheduleSource(scheduler, event_producer)

    signal.signal(signal.SIGINT, lambda *_: scheduler.shutdown())
    signal.signal(signal.SIGTERM, lambda *_: scheduler.shutdown())

    scheduler.start()

    LOG.info("Exiting...")
    event_producer.disconnect()


if __name__ == "__main__":
    main()
