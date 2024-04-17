__all__ = [
    "BatchPipelineMixin",
    "ComponentMixin",
    "EventBaseMixin",
    "InstanceRef",
    "JourneyMixin",
    "JourneysMixin",
    "InstanceRefSchema",
    "ProjectMixin",
    "RunMixin",
    "TaskMixin",
]

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum as std_Enum
from functools import partial
from typing import Optional
from uuid import UUID
from uuid import UUID as std_UUID
from uuid import uuid4

from marshmallow import Schema
from marshmallow.fields import UUID as m_UUID

from common.decorators import cached_property
from common.entities import ComponentType, Pipeline, Project, Run, RunTask, Task


@dataclass(kw_only=True)
class ProjectMixin:
    project_id: UUID

    @cached_property
    def project(self) -> Project:
        _project: Project = Project.get_by_id(self.project_id)
        return _project

    @property
    def partition_identifier(self) -> str:
        """Implementing the common.kafka.topic.PayloadInterface protocol."""
        return str(self.project_id)


@dataclass(kw_only=True)
class ComponentMixin:
    component_id: Optional[UUID] = None
    component_type: Optional[ComponentType] = None


@dataclass(kw_only=True)
class BatchPipelineMixin:
    batch_pipeline_id: Optional[UUID] = None
    run_id: Optional[UUID] = None

    @cached_property
    def batch_pipeline(self) -> Pipeline:
        _batch: Pipeline = Pipeline.get_by_id(self.batch_pipeline_id)
        return _batch

    @cached_property
    def run(self) -> Run:
        _run: Run = Run.get_by_id(self.run_id)
        return _run


@dataclass(kw_only=True)
class RunMixin:
    run_id: Optional[UUID] = None


@dataclass(kw_only=True)
class TaskMixin:
    task_id: Optional[UUID] = None
    run_task_id: Optional[UUID] = None

    @cached_property
    def task(self) -> Task:
        _task: Task = Task.get_by_id(self.task_id)
        return _task

    @cached_property
    def run_task(self) -> RunTask:
        _run_task: RunTask = RunTask.get_by_id(self.run_task_id)
        return _run_task


class InstanceType(std_Enum):
    DEFAULT = "DEFAULT"
    PAYLOAD = "PAYLOAD"


@dataclass
class InstanceRef:
    journey: std_UUID
    instance: std_UUID
    instance_type: InstanceType = InstanceType.DEFAULT


class InstanceRefSchema(Schema):
    journey_id = m_UUID(required=True)
    instance_id = m_UUID(required=True)


@dataclass(kw_only=True)
class JourneysMixin:
    instances: list[InstanceRef] = field(default_factory=list)


@dataclass(kw_only=True)
class JourneyMixin:
    journey_id: Optional[UUID] = None
    instance_id: Optional[UUID] = None


@dataclass(kw_only=True)
class EventBaseMixin:
    event_id: UUID = field(default_factory=uuid4)
    created_timestamp: datetime = field(default_factory=partial(datetime.now, tz=timezone.utc))
