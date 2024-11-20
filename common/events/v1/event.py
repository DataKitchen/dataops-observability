from __future__ import annotations

__all__ = ["Event", "EventInterface", "EVENT_ATTRIBUTES"]

import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from common.decorators import cached_property
from common.entities import (
    Component,
    ComponentType,
    Dataset,
    Instance,
    InstanceRule,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Project,
    Run,
    RunTask,
    Server,
    StreamingPipeline,
    Task,
)
from common.entities.event import EventVersion
from common.events.base import InstanceRef
from common.events.event_handler import EventHandlerBase
from common.events.v1.event_interface import EventInterface
from common.events.v1.event_schemas import EventApiSchema

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class EventComponentDetails:
    component_type: ComponentType
    prefix: InitVar[str]
    component_model: type[Component]
    component_id: str = field(init=False)
    component_key: str = field(init=False)
    component_name: str = field(init=False)

    def __post_init__(self, prefix: str) -> None:
        object.__setattr__(self, "component_id", prefix + "_id")
        object.__setattr__(self, "component_key", prefix + "_key")
        object.__setattr__(self, "component_name", prefix + "_name")


PIPELINE_KEY_DETAILS = EventComponentDetails(ComponentType.BATCH_PIPELINE, "pipeline", Pipeline)
DATASET_KEY_DETAILS = EventComponentDetails(ComponentType.DATASET, "dataset", Dataset)
SERVER_KEY_DETAILS = EventComponentDetails(ComponentType.SERVER, "server", Server)
STREAM_KEY_DETAILS = EventComponentDetails(ComponentType.STREAMING_PIPELINE, "stream", StreamingPipeline)

EVENT_ATTRIBUTES: dict[str, EventComponentDetails] = {
    "pipeline_key": PIPELINE_KEY_DETAILS,
    "dataset_key": DATASET_KEY_DETAILS,
    "server_key": SERVER_KEY_DETAILS,
    "stream_key": STREAM_KEY_DETAILS,
}
"""This is used to reference the corresponding component key and other component attributes in testing"""


@dataclass
class Event(EventInterface):
    """
    This is the base of all Event classes for the system, and should never be needed directly. Inherit from
    this to define your own Event to ensure your events have all the expected fields.
    """

    pipeline_key: Optional[str]
    source: str
    event_id: UUID
    event_timestamp: datetime
    received_timestamp: datetime
    metadata: dict[str, object]
    event_type: str
    run_name: Optional[str]
    run_key: Optional[str]
    component_tool: Optional[str]
    project_id: Optional[UUID]
    run_id: Optional[UUID]
    pipeline_id: Optional[UUID]
    task_id: Optional[UUID]
    task_name: Optional[str]
    task_key: Optional[str]
    run_task_id: Optional[UUID]
    external_url: Optional[str]
    pipeline_name: Optional[str]
    instances: list[InstanceRef]
    dataset_id: Optional[UUID]
    dataset_key: Optional[str]
    dataset_name: Optional[str]
    server_id: Optional[UUID]
    server_key: Optional[str]
    server_name: Optional[str]
    stream_id: Optional[UUID]
    stream_key: Optional[str]
    stream_name: Optional[str]
    payload_keys: list[str]
    version: EventVersion

    @property
    def partition_identifier(self) -> str:
        if self.project_id is None:
            raise ValueError("This event is not set up with a partition id")
        return str(self.project_id)

    @classmethod
    def as_event_from_request(cls, request_body: dict) -> Event:
        """
        Creates an "unidentified" instance of the Event from a request-body.

        Note: When we say unidentified, we mean that while we know its _type_, we do not know things like
        its task_id, run_task_id, and other such information. It's place has not been identified. This
        format allows the run manager to handle the incoming unidentified events the same way, as it builds them.
        """
        if cls.__api_schema__ is EventApiSchema:
            raise AttributeError("Subclasses of Event must define its own '__api_schema__'")

        # we have to shape the data here, and thus we need to validate the fields before we touch them.
        cls.__api_schema__().load(request_body)

        # Modifying the request body is probably undesirable, especially for testing purposes.
        event_body = dict.copy(request_body)

        # At a glance, we could have these defaulted by the schema. However, the spec says that if timestamp is not
        # defined, it _must_ be matched to the received time. Setting it in the schema would generate very tiny
        # differences in time.
        current_time = str(datetime.now(timezone.utc))
        if "event_timestamp" not in event_body:
            event_body["event_timestamp"] = current_time
        event_body["received_timestamp"] = current_time

        event_body["event_type"] = cls.__name__
        # We want to be able to trace an event through the system, and give an ID to the user. We'd thought
        # to use the elastic ID, but decided for a full through-put, a separate ID was more useful.
        event_body["event_id"] = uuid4()

        result: Event = cls.from_dict(event_body)
        return result

    def accept(self, handler: EventHandlerBase) -> bool:
        """
        Implement for each Event subtype. Call the appropriate handler
        function.
        """
        raise NotImplementedError

    @cached_property
    def task(self) -> Task:
        _task: Task = Task.get_by_id(self.task_id)
        return _task

    @cached_property
    def run_task(self) -> RunTask:
        _run_task: RunTask = RunTask.get_by_id(self.run_task_id)
        return _run_task

    @cached_property
    def run(self) -> Run:
        _run: Run = Run.get_by_id(self.run_id)
        return _run

    @cached_property
    def pipeline(self) -> Pipeline:
        _pipeline: Pipeline = Pipeline.get_by_id(self.pipeline_id)
        return _pipeline

    @cached_property
    def project(self) -> Project:
        _project: Project = Project.get_by_id(self.project_id)
        return _project

    @property
    def component_journeys(self) -> list[Journey]:
        """Select all Journeys that include event.component_id in the DAG."""
        jq = (
            Journey.select(Journey)
            .join(JourneyDagEdge)
            .join(
                Component,
                on=(JourneyDagEdge.right == Component.id) | (JourneyDagEdge.left == Component.id),
            )
            .where(Component.id == self.component_id)
            .distinct()
        )

        iq = Instance.select().where(Instance.active == True)
        prefetch_queries = [iq, InstanceRule]
        if self.run_id:
            # Select all the Journeys' Instances that either includes event.run_id or are active
            # The Instance subquery is split into two because doing a single query with an or-condition hurts performance a
            # lot.
            iq2 = (
                Instance.select(Instance.id)
                .left_outer_join(InstancesInstanceSets)
                .left_outer_join(InstanceSet)
                .left_outer_join(Run)
                .where(Run.id == self.run_id)
            )
            prefetch_queries = [
                Instance.select().where(Instance.id.in_(iq.select(Instance.id) | iq2)),
                InstancesInstanceSets.select().join(InstanceSet).join(Run).where(Run.id == self.run_id),
                InstanceRule,
            ]

        journeys: list[Journey] = jq.prefetch(*prefetch_queries)
        return journeys

    @cached_property
    def component_key_details(self) -> EventComponentDetails:
        if not (key := next((attr for attr in EVENT_ATTRIBUTES.keys() if getattr(self, attr, None) is not None), None)):
            LOG.error(f"Event component key details cannot be parsed from the event information provided: " f"{self}")
            raise ValueError("Event component key details cannot be parsed.")
        return EVENT_ATTRIBUTES[key]

    @property
    def component_key(self) -> str:
        if not (key := getattr(self, self.component_key_details.component_key, "")):
            LOG.error(f"Component key cannot be empty: {self}")
            raise ValueError("Component key cannot be empty.")
        return key

    @property
    def component_id(self) -> Optional[UUID]:
        return getattr(self, self.component_key_details.component_id, None)

    @component_id.setter
    def component_id(self, component_id: str) -> None:
        setattr(self, self.component_key_details.component_id, component_id)

    @component_id.setter
    def component_id(self, value: UUID) -> None:
        setattr(self, self.component_key_details.component_id, value)

    @property
    def component_name(self) -> Optional[str]:
        return getattr(self, self.component_key_details.component_name, None)

    @property
    def component_type(self) -> ComponentType:
        return self.component_key_details.component_type

    @property
    def component_model(self) -> type[Component]:
        return self.component_key_details.component_model

    @cached_property
    def component(self) -> Component:
        component: Component = self.component_model.get_by_id(self.component_id)
        return component
