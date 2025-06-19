__all__ = ["ScheduleSource", "RunTimeExecutor"]

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Protocol, TypeVar
from collections.abc import Callable

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.interval import IntervalTrigger

from common.kafka import KafkaProducer

LOG = logging.getLogger(__name__)

UPDATE_INTERVAL_SECONDS: int = 30


class RunTimeExecutor(ThreadPoolExecutor):
    """Executor that updates the job "run_time" kwarg before submitting it."""

    def submit_job(self, job: Job, run_times: list[datetime]) -> Any:
        if job.kwargs and "run_time" in job.kwargs:
            # We assume 'coalesce' is always True, and therefore there will be only one run_time value
            run_time = run_times[-1]
            job.modify(kwargs={**job.kwargs, "run_time": run_time})
            LOG.info("Job 'run_time' arg updated to '%s' for job '%s'", run_time, job.id)

        return super().submit_job(job, run_times)


class Schedule(Protocol):
    @property
    def id(self) -> str: ...


ST = TypeVar("ST", bound=Schedule)


class ScheduleSource[ST: Schedule]:
    """Concentrates all features and configurations around a specific source of schedules."""

    source_name: str
    """Used to name the specific stores and executors that are of exclusive use of this source."""

    def __init__(
        self, scheduler: BaseScheduler, event_producer: KafkaProducer, update_interval: int = UPDATE_INTERVAL_SECONDS
    ):
        self.scheduler = scheduler
        self.event_producer = event_producer
        self.scheduler.add_jobstore(MemoryJobStore(), self.jobstore_name)
        self.scheduler.add_executor(RunTimeExecutor(), self.executor_name)
        self.scheduler.add_job(self.update, trigger=IntervalTrigger(seconds=update_interval))
        self.update()

    @property
    def jobstore_name(self) -> str:
        return self.source_name

    @property
    def executor_name(self) -> str:
        return self.source_name

    def add_job(self, func: Callable, job_id: str, trigger: BaseTrigger, kwargs: dict[str, Any] | None) -> Job:
        return self.scheduler.add_job(
            func,
            id=job_id,
            trigger=trigger,
            kwargs=kwargs,
            jobstore=self.jobstore_name,
            executor=self.executor_name,
        )

    def update(self) -> None:
        """Sync scheduler `jobstore` data with db data"""
        LOG.debug("Started updating '%s' jobstore", self.jobstore_name)

        current_jobs = {j.id for j in self.scheduler.get_jobs(self.jobstore_name)}
        current_schedules = self._get_schedules()

        jobs_by_sched_id = defaultdict(list)
        for job_id in current_jobs:
            sched_id, _, _ = job_id.partition(":")
            jobs_by_sched_id[sched_id].append(job_id)

        LOG.debug(
            "Found %d jobs from %d schedules and %s schedules from the DB",
            len(current_jobs),
            len(jobs_by_sched_id),
            len(current_schedules),
        )

        for sched_id in jobs_by_sched_id.keys() - {str(s.id) for s in current_schedules}:
            for job_id in jobs_by_sched_id[sched_id]:
                LOG.info("Removing job ID '%s' from '%s' store", job_id, self.jobstore_name)
                self.scheduler.remove_job(job_id, jobstore=self.jobstore_name)

        new_schedules = [s for s in current_schedules if str(s.id) not in list(jobs_by_sched_id.keys())]
        for sched in new_schedules:
            LOG.info("Adding '%s' ID '%s' into '%s' store", type(sched).__name__, sched.id, self.jobstore_name)
            self._create_and_add_job(sched)

        LOG.debug("Completed updating '%s' jobstore", self.jobstore_name)

    def _create_and_add_job(self, schedule: ST) -> None:
        """Create and add new scheduler job(s) based on schedule expectations or instance rule"""
        raise NotImplementedError

    def _get_schedules(self) -> list[ST]:
        """Retrieve schedules from database"""
        raise NotImplementedError
