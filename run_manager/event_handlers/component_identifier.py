__all__ = ["ComponentIdentifier"]

import logging
from typing import cast

from peewee import DoesNotExist

from common.entities import Component, ComponentType, Dataset, Pipeline, Project, Server, StreamingPipeline
from common.events import EventHandlerBase
from common.events.v1 import (
    DatasetOperationEvent,
    Event,
    MessageLogEvent,
    MetricLogEvent,
    RunStatusEvent,
    TestOutcomesEvent,
)
from run_manager.context import RunManagerContext

LOG = logging.getLogger(__name__)

ALL_COMPONENTS = (Pipeline, Dataset, Server, StreamingPipeline)

COMPONENT_TYPES = {class_.component_type: class_ for class_ in ALL_COMPONENTS}
"""Map event component type to db model"""


def _get_component(event: Event) -> Component | None:
    # v1 event can only have one (component type)_id
    if component_id := event.component_id:
        try:
            component: Component = event.component_model.get_by_id(component_id)
            return component
        except DoesNotExist:
            LOG.warning(f"No {event.component_type} exist with id: {component_id}")
            raise
    try:
        project = Project.get_by_id(event.project_id)
    except DoesNotExist:
        LOG.warning("No project exist with project id: %s", event.project_id)
        raise
    try:
        component_key = event.component_key
        component = event.component_model.get(
            event.component_model.key == component_key, event.component_model.project == project.id
        )
    except DoesNotExist:
        return None

    LOG.info("Retrieved existing component with id '%s'", component.id)
    if (new_component_name := event.component_name) and new_component_name != component.name:
        component.name = new_component_name
    if (new_component_tool := event.component_tool) and new_component_tool != component.tool:
        component.tool = new_component_tool
    component.save()
    return component


def _create_component(event: Event) -> Component | None:
    component: Component = event.component_model.create(
        key=event.component_key, name=event.component_name, tool=event.component_tool, project_id=event.project_id
    )
    LOG.info(f"Created new {event.component_type} component with id `{component.id}`")
    return component


class ComponentIdentifier(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context

    def handle_message_log(self, event: MessageLogEvent) -> bool:
        self._handle_event(event)
        return True

    def handle_metric_log(self, event: MetricLogEvent) -> bool:
        self._handle_event(event)
        return True

    def handle_run_status(self, event: RunStatusEvent) -> bool:
        self._handle_event(event)
        return True

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        self._handle_event(event)
        return True

    def handle_dataset_operation(self, event: DatasetOperationEvent) -> bool:
        self._handle_event(event)
        return True

    def _handle_event(self, event: Event) -> None:
        try:
            component = _get_component(event) or _create_component(event)
            self.context.component = component
        except DoesNotExist:
            return

        if event.component_type == ComponentType.BATCH_PIPELINE:
            self.context.pipeline = cast(Pipeline, component)
