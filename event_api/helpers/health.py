from common.entities import DB
from common.kafka import TOPIC_UNIDENTIFIED_EVENTS, KafkaProducer
from common.kubernetes.readiness_probe import NotReadyException


def readiness_probe() -> None:
    if DB.obj is None:
        raise NotReadyException("Database not initialized")
    with KafkaProducer({}) as producer:
        if not producer.is_topic_available(TOPIC_UNIDENTIFIED_EVENTS):
            raise NotReadyException("Kafka topic not ready or producer not connected")
