__all__ = ["ScheduleType"]

from enum import Enum


class ScheduleType(Enum):
    BATCH_START_TIME = "BATCH_START_TIME"
    BATCH_START_TIME_MARGIN = "BATCH_START_TIME_MARGIN"
    BATCH_END_TIME = "BATCH_END_TIME"
    DATASET_ARRIVAL_MARGIN = "DATASET_ARRIVAL_MARGIN"


class EventSources(Enum):
    API = "API"
    USER = "USER"
    SCHEDULER = "SCHEDULER"
    RULES_ENGINE = "RULES_ENGINE"
    # This last one should be considered a bug if seen in the wild. But it can be used as a dumb-default for tracing.
    UNKNOWN = "UNKNOWN"
