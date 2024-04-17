from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from common.kafka.topic import MixedTopic, PayloadInterface
from testlib.fixtures.v1_events import *


@dataclass
class TestClass(PayloadInterface):
    a: str

    @property
    def partition_identifier(self) -> str:
        return self.a


@pytest.fixture
def a_dataclass():
    return TestClass(a="Safe economy or test executive")


@pytest.mark.integration
def test_mixed_topic_serialize_v1_events(message_log_event, mocked_kafka_message):
    topic = MixedTopic(name="reflect")

    msg_args = topic.serialize(message_log_event)
    assert isinstance(msg_args.value.decode("utf-8"), str)
    assert len(msg_args.headers) == 0

    mocked_kafka_message.value = Mock(return_value=msg_args.value)
    mocked_kafka_message.headers = Mock(return_value=msg_args.headers)
    msg = topic.deserialize(mocked_kafka_message)
    assert msg.payload == message_log_event


@pytest.mark.integration
def test_mixed_topic_serialize_others_events(a_dataclass, mocked_kafka_message):
    topic = MixedTopic(name="reflect")

    msg_args = topic.serialize(a_dataclass)
    with pytest.raises(ValueError):
        msg_args.value.decode("utf-8")
    assert len(msg_args.headers) > 0
    print(msg_args.headers)

    mocked_kafka_message.value = Mock(return_value=msg_args.value)
    mocked_kafka_message.headers = Mock(return_value=[(k, v.encode("utf-8")) for k, v in msg_args.headers.items()])
    msg = topic.deserialize(mocked_kafka_message)
    assert msg.payload == a_dataclass
