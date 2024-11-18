from typing import Any

from .dataset_operation_event import *
from .event import *
from .event_interface import *
from .event_schemas import *
from .message_log_event import *
from .metric_log_event import *
from .run_status_event import *
from .test_outcomes_event import *

# NOTE: If you forget to import an Event class above, it will NOT show up in this list!
EVENT_TYPE_MAP: dict[str, type[EventInterface]] = {
    **{s.__name__: s for s in Event.__subclasses__()},
}

# NOTE: This is needed for the Swagger Docs. For each new event type, we will need to add to this list if we want to
# generate documentation for it.
ALL_API_EVENT_SCHEMAS = [
    DatasetOperationApiSchema,
    MessageLogEventApiSchema,
    MetricLogApiSchema,
    RunStatusApiSchema,
    TestOutcomesApiSchema,
]

ALL_EVENT_SCHEMAS = [
    DatasetOperationSchema,
    MessageLogEventSchema,
    MetricLogSchema,
    RunStatusSchema,
    TestOutcomesSchema,
]


def instantiate_event_from_data(event_data: dict[str, Any]) -> Any:
    """
    Given a dict representation of an event, it pulls the information necessary from the event data
    to instantiate the correct Event child
    """
    event_type: type[EventInterface] = EVENT_TYPE_MAP[event_data["event_type"]]
    return event_type.from_dict(data=event_data)
