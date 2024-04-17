__all__ = ["RunManagerContext"]
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from common.entities import Component, Instance, InstanceSet, Pipeline, Run, RunTask, Task
from common.events.base import InstanceRef, InstanceType


@dataclass
class RunManagerContext:
    """
    A context object to pass a state around when handling events in run manager
    """

    component: Optional[Component] = None
    # Keeping pipeline to keep "pre" event v1 code intact, i.e. avoid significant refactoring effort
    pipeline: Optional[Pipeline] = None
    run: Optional[Run] = None
    task: Optional[Task] = None
    run_task: Optional[RunTask] = None
    instances: list[InstanceRef] = field(default_factory=list)
    instance_set: Optional[InstanceSet] = None
    ended_instances: list[UUID | Instance] = field(default_factory=list)
    """List of instances that ended in this context"""
    created_run: bool = False
    """Indicates if the run was created during this context"""
    started_run: bool = False
    """Indicates if the run was started during this context"""
    prev_run_status: Optional[str] = None
    """Previous run status before being processed by the run handler.
       This is to check for unexpected run status changed"""

    @property
    def instance_ids(self) -> list[UUID]:
        return [ref.instance for ref in self.instances]

    @property
    def instances_dict(self) -> dict[InstanceType, dict[str, list[InstanceRef | UUID]]]:
        res: dict[InstanceType, dict[str, list[InstanceRef | UUID]]] = {
            InstanceType.DEFAULT: {"instance_refs": [], "ids": []},
            InstanceType.PAYLOAD: {"instance_refs": [], "ids": []},
        }
        for instance_ref in self.instances:
            res[instance_ref.instance_type]["instance_refs"].append(instance_ref)
            res[instance_ref.instance_type]["ids"].append(instance_ref.instance)
        return res
