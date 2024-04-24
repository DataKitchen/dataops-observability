INVALID_INT_TYPE = "Not a valid integer."
INVALID_STR_TYPE = "Not a valid string."
MISSING_REQUIRED_FIELD = "Missing data for required field."
UNKNOWN_FIELD = "Unknown field."
NULL_FIELD = "Field may not be null."
INVALID_TIMEZONE = "Not a valid timezone."
INVALID_SCHEDULE_MARGIN = "Only values above 0 and multiples of 60 (one minute) are accepted."
MISSING_COMPONENT_KEY = "There must be at least one valid component key specified."
PIPELINE_EVENT_MISSING_REQUIRED_KEY = (
    "Event with batch-pipeline component must have both `pipeline_key` and `run_key` fields specified. "
)
RUNSTATUS_EVENT_MISSING_REQUIRED_KEY = "RunStatusEvent must have both `pipeline_key` and `run_key` fields set."
INVALID_TOOL_VALUE = "Tool must be alphanumeric including underscore and space. Underscore may not be leading/trailing"
