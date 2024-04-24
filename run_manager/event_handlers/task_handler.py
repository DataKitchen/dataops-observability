__all__ = ["TaskHandler"]
import logging
from typing import Union, cast

from common.constants.peewee import BATCH_SIZE
from common.entities import RunTask, RunTaskStatus, Task
from common.events import EventHandlerBase
from common.events.v1 import MessageLogEvent, MetricLogEvent, RunStatusEvent, TestOutcomesEvent
from common.peewee_extensions.fields import UTCTimestampField
from run_manager.context import RunManagerContext
from run_manager.event_handlers.utils import update_state

LOG = logging.getLogger(__name__)
TaskEvent = Union[MessageLogEvent, MetricLogEvent, TestOutcomesEvent, RunStatusEvent]


class TaskHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context

    def _create_required_tasks(self) -> None:
        # Only create required tasks when the run is created
        if not self.context.created_run or self.context.pipeline is None:
            return
        run_tasks = [
            RunTask(run=self.context.run, task=task, required=True)
            for task in self.context.pipeline.pipeline_tasks.where(Task.required == True)
        ]
        RunTask.bulk_create(run_tasks, batch_size=BATCH_SIZE)
        LOG.debug("Created %s required run tasks", len(run_tasks))

    def _identify_task(self, event: TaskEvent) -> None:
        if not event.pipeline_id or not event.task_key:
            return

        task, created = Task.get_or_create(pipeline_id=event.pipeline_id, key=event.task_key)
        if created:
            LOG.info("Created new task '%s' in pipeline '%s'", event.task_key, event.pipeline_id)

        # If a task_name came in for an existing task but it has changed, consider it an update to task name. The name
        # is NOT used to lookup the task. Do not consider a change to None / empty.
        if (task_name := event.task_name) and task_name != task.name:
            task.name = task_name
            task.save()

        run_task, created = RunTask.get_or_create(run_id=event.run_id, task=task, defaults={"required": False})
        if created:
            LOG.info("Created new run task '%s' for task '%s'", run_task.id, task.id)

        self.context.task = task
        self.context.run_task = run_task

    def _handle_task_event(self, event: TaskEvent) -> None:
        self._create_required_tasks()
        self._identify_task(event)
        if (run_task := self.context.run_task) is None:
            return None

        if not run_task.start_time:
            run_task.start_time = cast(UTCTimestampField, event.event_timestamp)
        run_task.status = RunTaskStatus.max(run_task.status, RunTaskStatus.RUNNING.name).name
        run_task.save()

    def handle_message_log(self, event: MessageLogEvent) -> bool:
        self._handle_task_event(event)
        return True

    def handle_metric_log(self, event: MetricLogEvent) -> bool:
        self._handle_task_event(event)
        return True

    def _handle_task_status(self, event: RunStatusEvent) -> None:
        self._identify_task(event)
        LOG.info("Processing run status task: %s", event.task_key)
        if (run_task := self.context.run_task) is None:
            LOG.error("Unable to find run_task to update.")
        else:
            update_state(run_task, event)
            run_task.save()

    def _handle_run_status(self, event: RunStatusEvent) -> None:
        if event.is_close_run:
            RunTask.update({RunTask.status: RunTaskStatus.MISSING.name}).where(
                RunTask.run == self.context.run, RunTask.status == RunTaskStatus.PENDING.name
            ).execute()
        else:
            RunTask.update({RunTask.status: RunTaskStatus.PENDING.name}).where(
                RunTask.run == self.context.run, RunTask.status == RunTaskStatus.MISSING.name
            ).execute()

    def handle_run_status(self, event: RunStatusEvent) -> bool:
        self._create_required_tasks()
        # No task_key means it's not a task event
        if event.task_key is None:
            self._handle_run_status(event)
        else:
            self._handle_task_status(event)

        return True

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        self._handle_task_event(event)
        return True
