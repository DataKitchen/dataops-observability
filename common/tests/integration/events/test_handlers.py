import pytest

from common.events import EventHandlerBase
from common.events.v1 import (
    DatasetOperationEvent,
    Event,
    EventSchema,
    MessageLogEvent,
    MetricLogEvent,
    RunStatusEvent,
    TestOutcomesEvent,
)


class TestEventSchema(EventSchema):
    pass


class TestEvent(Event):
    __schema__ = TestEventSchema


class TestHandler(EventHandlerBase):
    def handle_run_status(self, event) -> bool:
        assert event.__class__ is RunStatusEvent
        return True

    def handle_message_log(self, event) -> bool:
        assert event.__class__ is MessageLogEvent
        return True

    def handle_metric_log(self, event) -> bool:
        assert event.__class__ is MetricLogEvent
        return True

    def handle_test_outcomes(self, event) -> bool:
        assert event.__class__ is TestOutcomesEvent
        return True

    def handle_dataset_operation(self, event) -> bool:
        assert event.__class__ is DatasetOperationEvent
        return True


@pytest.mark.integration
def test_base_event_handler(event_data):
    with pytest.raises(NotImplementedError):
        TestEvent(**event_data, event_type="TestEvent").accept(TestHandler())


@pytest.mark.integration
def test_close_run_event_handler(COMPLETED_run_status_event):
    COMPLETED_run_status_event.accept(TestHandler())


@pytest.mark.integration
def test_message_log_event_handler(message_log_event):
    message_log_event.accept(TestHandler())


@pytest.mark.integration
def test_metric_log_event_handler(metric_log_event):
    metric_log_event.accept(TestHandler())


@pytest.mark.integration
def test_run_status_event_handler(RUNNING_run_status_event):
    RUNNING_run_status_event.accept(TestHandler())


@pytest.mark.integration
def test_test_outcomes_event_handler(test_outcomes_event):
    test_outcomes_event.accept(TestHandler())


@pytest.mark.integration
def test_dataset_operation_event_handler(dataset_operation_event):
    dataset_operation_event.accept(TestHandler())
