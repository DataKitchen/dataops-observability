from unittest.mock import patch, Mock

import pytest
from confluent_kafka.cimpl import NewTopic, KafkaException, KafkaError

from common.kafka.admin import create_topics
from common.kafka.topic import Topic


@pytest.fixture
def client_class_mock():
    with patch("common.kafka.admin.AdminClient") as mock:
        yield mock


@pytest.fixture
def client_mock(client_class_mock):
    mock = Mock()
    client_class_mock.return_value = mock
    yield mock


@pytest.fixture
def create_topics_mock(client_mock):
    yield client_mock.create_topics


@pytest.fixture
def result_mock(create_topics_mock):
    future_mock = Mock()
    result_mock = future_mock.result
    create_topics_mock.return_value = {"TEST_TOPIC": future_mock}
    yield result_mock


@pytest.fixture
def topic():
    return Topic(name="TEST_TOPIC")


@pytest.mark.unit
@pytest.mark.parametrize("result_side_effect", (lambda: None, KafkaException(KafkaError.TOPIC_ALREADY_EXISTS)))
def test_create_topics(result_side_effect, client_class_mock, create_topics_mock, result_mock, topic):
    result_mock.side_effect = result_side_effect

    create_topics([topic], num_partitions=5, replication_factor=5)

    client_class_mock.assert_called_once()
    create_topics_mock.assert_called_once_with([NewTopic("TEST_TOPIC", num_partitions=5, replication_factor=5)])
    result_mock.assert_called_once()


@pytest.mark.unit
def test_create_topics_fail(client_class_mock, create_topics_mock, result_mock, topic):
    result_mock.side_effect = KafkaException(KafkaError.MEMBER_ID_REQUIRED)

    with pytest.raises(Exception):
        create_topics([topic], num_partitions=5, replication_factor=5)

    client_class_mock.assert_called_once()
    create_topics_mock.assert_called_once_with([NewTopic("TEST_TOPIC", num_partitions=5, replication_factor=5)])
    result_mock.assert_called_once()
