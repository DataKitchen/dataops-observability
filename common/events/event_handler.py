__all__ = ["EventHandlerBase"]

from typing import Any


class EventHandlerBase:
    """
    Implement Event type specific actions the corresponding visitor function using the visitor pattern.

    The handler function return True if handling the event was successful, False otherwise.

    Example usage:
    class ExampleHandler(EventHandlerBase):

        def handle_run_status(self, event: RunStatusEvent):
            LOG.info("Handling run status event")
            return True

    def process_event(event: Event):
        event.accept(ExampleHandler())
    """

    def handle_run_status(self, event: Any) -> bool:
        return True

    def handle_message_log(self, event: Any) -> bool:
        return True

    def handle_metric_log(self, event: Any) -> bool:
        return True

    def handle_test_outcomes(self, event: Any) -> bool:
        return True

    def handle_dataset_operation(self, event: Any) -> bool:
        return True

    def handle_batch_pipeline_status_v2_base(self, event: Any) -> bool:
        """
        Handle all run statuses, API ingested and internally generated.

        This functiona will not be called if one of the specific run status functions apply instead.
        """
        return True

    def handle_batch_pipeline_status_user_v2(self, event: Any) -> bool:
        return self.handle_batch_pipeline_status_v2_base(event)

    def handle_batch_pipeline_status_platform_v2(self, event: Any) -> bool:
        return self.handle_batch_pipeline_status_v2_base(event)

    def handle_dataset_operation_v2(self, event: Any) -> bool:
        return True

    def handle_message_log_v2(self, event: Any) -> bool:
        return True

    def handle_metric_log_v2(self, event: Any) -> bool:
        return True

    def handle_test_outcomes_v2(self, event: Any) -> bool:
        return True
