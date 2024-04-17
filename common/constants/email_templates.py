"""
ADDING A NEW TEMPLATE:
1) Work with the UI team on the new template, making sure they create an HTML _and_ a TEXT form of the template
2) Decide with the UI team on a good name for the template, using snake_case.
   It should be descriptive -- characters are cheap!
3) In your PR to add the functionality around the new template, add an entry to this file containing
   the name of the template.
     - Try to name each template with <SOMETHING>_TEMPLATE_NAME so that they read well when we invoke them elsewhere.
4) TEST YOUR TEMPLATE.  Send a dummy email to yourself from  using client.send_templated_email()
   and CONFIRM WITH THE UI TEAM that the look of the email is exactly right!
"""

INSTANCE_ALERT_TEMPLATE_NAME = "instance_alert"
MESSAGE_LOG_TEMPLATE_NAME = "message_log"
METRIC_LOG_TEMPLATE_NAME = "metric_log"
RUN_STATE_TEMPLATE_NAME = "run_state"
TASK_STATUS_COMPLETED_TEMPLATE_NAME = "task_status_completed"
TASK_STATUS_ERROR_TEMPLATE_NAME = "task_status_error"
TASK_STATUS_MISSING_TEMPLATE_NAME = "task_status_missing"
TASK_STATUS_PENDING_TEMPLATE_NAME = "task_status_pending"
TASK_STATUS_STARTED_TEMPLATE_NAME = "task_status_started"
TASK_STATUS_WARNING_TEMPLATE_NAME = "task_status_warning"
TEST_STATUS_TEMPLATE_NAME = "test_status"
