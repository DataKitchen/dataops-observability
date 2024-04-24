import pytest

from common.entities import Component, Pipeline
from run_manager.context import RunManagerContext
from run_manager.event_handlers.component_identifier import ComponentIdentifier
from testlib.fixtures.v1_events import *


@pytest.mark.integration
def test_component_identifier_no_name_or_tool_update(pipeline, run_status_event):
    pipeline.tool = "TEST_TOOL"
    pipeline.name = "test name"
    pipeline.save()

    identifier = ComponentIdentifier(RunManagerContext())
    run_status_event.accept(identifier)

    assert Component.select().count() == 1
    assert Pipeline.get().tool == pipeline.tool
    assert Pipeline.get().name == pipeline.name


@pytest.mark.integration
def test_component_identifier_create_component(run_status_event):
    run_status_event.component_tool = "TEST_TOOL"
    run_status_event.pipeline_name = "test name"

    identifier = ComponentIdentifier(RunManagerContext())
    run_status_event.accept(identifier)

    assert Component.select().count() == 1
    assert Pipeline.get().tool == run_status_event.component_tool
    assert Pipeline.get().name == run_status_event.pipeline_name


@pytest.mark.integration
def test_component_identifier_update_attributes(run_status_event, pipeline):
    pipeline.tool = "OLD_TOOL"
    pipeline.name = "old name"
    pipeline.save()
    run_status_event.component_tool = "NEW_TOOL"
    run_status_event.pipeline_name = "new name"

    identifier = ComponentIdentifier(RunManagerContext())
    run_status_event.accept(identifier)

    assert Component.select().count() == 1
    assert Pipeline.get().tool == run_status_event.component_tool
    assert Pipeline.get().name == run_status_event.pipeline_name
