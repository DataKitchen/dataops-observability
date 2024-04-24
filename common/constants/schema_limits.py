# NOTE: The value of 255 is used here because it matches the default length
# set by peewee's CharField object. Changing these values to greater than 255
# will require modifying the entity schemas.
# see: https://docs.peewee-orm.com/en/latest/peewee/api.html#CharField

MAX_EVENT_TYPE_LENGTH: int = 40
"""The max length of a event type."""

MAX_PIPELINE_KEY_LENGTH: int = 255
"""The max length of a pipeline key."""

MAX_TASK_KEY_LENGTH: int = 255
"""The max length of a task identification key."""

MAX_RUN_KEY_LENGTH: int = 255
"""The max length of a run key."""

MAX_STATE_LABEL_LENGTH: int = 255
"""The max length of state_label member."""

MAX_DESCRIPTION_LENGTH: int = 255
"""Normal max length of a description."""

MAX_COMPONENT_TOOL_LENGTH: int = 255
"""The component tool name max length"""

MAX_STATE_DESCRIPTION_LENGTH: int = MAX_DESCRIPTION_LENGTH
"""The max length of a state_description member."""

MAX_ACTION_IMPL_LENGTH: int = 50
"""The max length of an Action implementation."""

MAX_TEST_OUTCOME_NAME_LENGTH: int = 255
"""The max length of a test outcome name."""

MAX_SUBCOMPONENT_KEY_LENGTH: int = 255
"""The max length of a subcomponent key."""

MAX_COMPONENT_NAME_LENGTH: int = 255
"""The max length of a component name."""

MAX_TEST_OUTCOME_ITEM_COUNT: int = 500
"""The max amount of items in a TestOutcomes event."""

MAX_TASK_NAME_LENGTH: int = 255
"""The max length of a task name."""

MAX_RUN_NAME_LENGTH: int = 1024
"""The max length of a run name."""

MAX_PATH_LENGTH: int = 4096
"""The max length for a path-like field."""

MAX_CRON_EXPRESSION_LENGTH: int = 100
"""The max length for a cron expression field."""

MAX_TIMEZONE_LENGTH: int = 50
"""The max length for a timezone field."""

MAX_SERVICE_ACCOUNT_KEY_NAME_LENGTH: int = 255
"""The max length for the name of a service account key."""

MAX_SERVICE_ACCOUNT_KEY_DESCRIPTION_LENGTH: int = 255
"""The max length for a service account key description."""

MAX_TEST_OUTCOME_KEY_LENGTH: int = 255
"""The max length of a test outcome identification key."""

MAX_TEST_OUTCOME_TYPE_LENGTH: int = 40
"""The max length of a test outcome type identifier."""

MAX_PAYLOAD_KEY_LENGTH: int = 255
"""The max length of a payload key."""
