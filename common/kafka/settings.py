# Settings module for Kafka

# Settings

KAFKA_OP_TIMEOUT_SECS: int = 10
"""How long to wait for general operations to complete."""

KAFKA_TX_TIMEOUT_MILISECS: int = 30000
"""How long a transaction block can last. If the transaction stays open for longer than this period it will fail"""

PRODUCER_TX_OPS_TIMEOUT_SECS: float = 5
"""How long to wait for the transactional operations."""

PRODUCER_TX_COMMIT_TIMEOUT_SECS: int = 6
"""How long to wait for commit operation."""

PRODUCER_MANDATORY_SETTINGS = {
    "request.required.acks": "all",
}
"""Settings that must be the same across all producers."""

PRODUCER_TX_MANDATORY_SETTINGS = {
    "enable.idempotence": True,
    "transaction.timeout.ms": KAFKA_TX_TIMEOUT_MILISECS,
}
"""Settings that must be the same across all _transactional_ producers."""

CONSUMER_POLL_PERIOD_SECS = 5
"""How long the consumer should block on the .poll() call waiting for a message."""

CONSUMER_TX_MANDATORY_SETTINGS = {"isolation.level": "read_committed", "enable.auto.commit": False}
"""Settings that must be the same across all _transactional_ consumers."""
