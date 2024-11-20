__all__ = ["RunService"]

from uuid import UUID

from peewee import prefetch

from common.entities import Run, RunTask, Task
from common.entity_services.helpers import ListRules, Page, SortOrder


class RunService:
    @staticmethod
    def get_runtasks_with_rules(run_id: UUID, rules: ListRules) -> Page[RunTask]:
        # Typically, we'd sort these by name, but as this will be used in a DAG (Directed Acyclic Graph),
        # we sort instead by Start Time.
        # TODO: Support Pagination. Note: Update the swagger doc when this is done.
        results = (
            RunTask.select()
            .join(Run)
            .where(Run.id == run_id)
            .order_by(RunTask.start_time.asc() if rules.sort == SortOrder.ASC else RunTask.start_time.desc())
        )
        fetched_result: list[RunTask] = prefetch(results, Task.select(Task.id, Task.key, Task.name))
        return Page[RunTask](results=fetched_result, total=results.count())
