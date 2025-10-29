import logging

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException, KafkaError

from common.kafka.topic import Topic
from conf import settings

LOG = logging.getLogger(__name__)


def create_topics(topics: list[Topic], num_partitions: int = 1, replication_factor: int = 1) -> None:
    client = AdminClient(settings.KAFKA_CONNECTION_PARAMS)
    new_topics = [
        NewTopic(topic.name, num_partitions=num_partitions, replication_factor=replication_factor) for topic in topics
    ]
    failed_topics = []
    for topic_name, future in client.create_topics(new_topics).items():
        try:
            future.result()
        except KafkaException as e:
            if e.args[0] != KafkaError.TOPIC_ALREADY_EXISTS:
                failed_topics.append(topic_name)
        except Exception:
            LOG.exception("Error creating %s Kafka topic", topic_name)
            failed_topics.append(topic_name)

    if failed_topics:
        raise Exception(f"Creating the topics {", ".join(failed_topics)} failed.")
