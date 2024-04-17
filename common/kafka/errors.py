class MessageError(Exception):
    """An error with the message itself, not an issue with Kafka"""


class InvalidHeadersError(MessageError):
    pass


class DeserializationError(MessageError):
    pass


class SerializationError(MessageError):
    pass


class MessageTooLargeError(MessageError):
    pass


class ProducerError(Exception):
    pass


class ProducerTransactionError(ProducerError):
    pass


class DisconnectedProducerError(ProducerError):
    pass


class ProducerConfigurationError(ProducerError):
    pass


class ConsumerError(Exception):
    pass


class ConsumerConfigurationError(ConsumerError):
    pass


class DisconnectedConsumerError(ConsumerError):
    pass


class ConsumerCommitError(ConsumerError):
    pass
