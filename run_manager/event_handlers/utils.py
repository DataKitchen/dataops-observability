import logging
from typing import Union, cast

from common.entities import Run, RunStatus, RunTask
from common.events.v1 import RunStatusEvent
from common.peewee_extensions.fields import UTCTimestampField

LOG = logging.getLogger(__name__)


def update_state(entity: Union[Run, RunTask], event: RunStatusEvent) -> None:
    """
    Update the given entity according to the information in the event

    * Always decrease the entity start time if an earlier time is found
    * A new end time and status is only set if the event is newer than current end time
    * The end time is cleared if the even has a newer running status than current end time.
    * End time and status is always set/cleared if no end time is set.
    """
    if entity.start_time is None or entity.start_time > event.event_timestamp:
        entity.start_time = cast(UTCTimestampField, event.event_timestamp)
    if RunStatus.is_end_status(event.status):
        if entity.end_time is None or entity.end_time < event.event_timestamp:
            LOG.info("Closing %s '%s'", entity.__class__.__name__, entity.id)
            entity.end_time = cast(UTCTimestampField, event.event_timestamp)
            entity.status = event.status
    elif entity.end_time is None or entity.end_time < event.event_timestamp:
        entity.end_time = cast(UTCTimestampField, None)
        entity.status = event.status
