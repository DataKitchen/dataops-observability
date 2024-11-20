__all__ = ["InstanceHandler"]
import logging
from collections import defaultdict
from itertools import chain
from typing import Any, Optional, cast
from collections.abc import Callable, Mapping
from uuid import UUID

from common.constants.peewee import BATCH_SIZE
from common.entities import (
    Instance,
    InstanceRule,
    InstanceRuleAction,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    Run,
    RunStatus,
)
from common.entities.instance import InstanceStartType
from common.entity_services import InstanceService
from common.events import EventHandlerBase
from common.events.base import InstanceRef, InstanceType
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


def _find_existing_instance(journey: Journey, with_run: bool, payload_key: Optional[str]) -> Optional[Instance]:
    if payload_key is None:
        f: Callable[[Any], bool | Any] = lambda k: k.payload_key is None
    else:
        f = lambda k: k.payload_key == payload_key
    instances = list(filter(f, (instance for instance in journey.instances)))

    # First check if the run is assigned to an instance already, next best
    # is to find an active instance instead.
    def has_runs(instance: Any) -> bool:
        return len(instance.iis) > 0

    def is_active(instance: Any) -> bool:
        return instance.active is True

    filters = [filter(is_active, instances)]
    if with_run:
        filters.insert(0, filter(has_runs, instances))

    return next(
        chain(*filters),
        None,
    )


def _get_run_instances(run: Run) -> list[Instance]:
    """Get all instances associate with the run from its instance set if available"""
    return list(Instance.select().join(InstancesInstanceSets).join(InstanceSet).join(Run).where(Run.id == run))


def _make_instance_ref(instance: Instance) -> InstanceRef:
    """Create InstanceRef from Instance"""
    return InstanceRef(
        journey=instance.journey_id,
        instance=instance.id,
        instance_type=InstanceType.PAYLOAD if instance.payload_key else InstanceType.DEFAULT,
    )


class InstanceHandler(EventHandlerBase):
    def __init__(self, context: RunManagerContext):
        self.context = context

    def set_instance_set(self) -> None:
        if self.context.instances:
            self.context.instance_set = InstanceSet.get_or_create([ir.instance for ir in self.context.instances])
            if self.context.run and self.context.run.instance_set_id != self.context.instance_set.id:
                self.context.run.instance_set = self.context.instance_set
                self.context.run.save()

    def set_instances(self, event: Event) -> None:
        if self.context.created_run:
            self.apply_instance_start_rules(event)

        # Reuse instances for already started runs
        if not self.context.run or self.context.started_run or self.context.created_run:
            self.context.instances = self.default_instance_creation(event)
        else:
            self.context.instances = list(map(_make_instance_ref, _get_run_instances(self.context.run)))
        self.set_instance_set()

    def handle_message_log(self, event: MessageLogEvent) -> bool:
        self.set_instances(event)
        return True

    def handle_metric_log(self, event: MetricLogEvent) -> bool:
        self.set_instances(event)
        return True

    def handle_run_status(self, event: RunStatusEvent) -> bool:
        self.set_instances(event)
        if event.is_close_run:
            instance_rules = InstanceRule.select().where(
                InstanceRule.journey.in_([ref.journey for ref in self.context.instances]),
            )
            end_rules = []
            instance_types = set()
            journey_rules: defaultdict[UUID, list[InstanceRule]] = defaultdict(list)
            for rule in instance_rules:
                # END_PAYLOAD rule doesn't affect the default instance ending behavior
                if rule.action != InstanceRuleAction.END_PAYLOAD:
                    journey_rules[rule.journey_id].append(rule)
                if rule.batch_pipeline_id == event.pipeline_id and rule.action == InstanceRuleAction.END:
                    end_rules.append(rule)
                    instance_types.add(InstanceType.DEFAULT)
                elif rule.batch_pipeline_id == event.pipeline_id and rule.action == InstanceRuleAction.END_PAYLOAD:
                    end_rules.append(rule)
                    instance_types.add(InstanceType.PAYLOAD)
            if len(end_rules) > 0:
                assert self.context.run is not None
                instance_ids = list(chain(*[self.context.instances_dict[t]["ids"] for t in instance_types]))
                ended_instances = list(
                    Instance.select()
                    .where(
                        Instance.journey.in_([rule.journey_id for rule in end_rules])
                        & Instance.id.in_(instance_ids)
                        & Instance.end_time.is_null()
                    )
                    .execute()
                )
                count = (
                    Instance.update({Instance.end_time: event.event_timestamp})
                    .where(Instance.id.in_(ended_instances))
                    .execute()
                )
                LOG.info("%s closed %d instance(s)", end_rules, count)
                self.context.ended_instances.extend(ended_instances)
            self.close_finished_instances(
                event,
                cast(list[InstanceRef], self.context.instances_dict[InstanceType.DEFAULT]["instance_refs"]),
                journey_rules,
            )

        return True

    def handle_test_outcomes(self, event: TestOutcomesEvent) -> bool:
        self.set_instances(event)
        return True

    def handle_dataset_operation(self, event: DatasetOperationEvent) -> bool:
        self.set_instances(event)
        return True

    def apply_instance_start_rules(self, event: Event) -> None:
        event_journeys = event.component_journeys  # Stashed result to avoid repeating query
        start_rules = (
            InstanceRule.select()
            .where(
                (InstanceRule.journey.in_(event_journeys))
                & (InstanceRule.batch_pipeline == event.pipeline_id)
                & (InstanceRule.action == InstanceRuleAction.START)
            )
            .execute()
        )

        journey_ids = [x.journey_id for x in start_rules]
        # Instance START rule doesn't affect payload instances
        instances: list[Instance] = list(
            filter(
                lambda i: (i.payload_key is None and i.end_time is None),
                sum([j.instances for j in event_journeys if j.id in journey_ids], []),
            )
        )
        new_instances = []
        for rule in start_rules:
            new_instance = Instance(
                journey_id=rule.journey_id, start_time=event.event_timestamp, start_type=InstanceStartType.BATCH
            )
            new_instances.append(new_instance)
        Instance.bulk_create(new_instances, batch_size=BATCH_SIZE)

        Instance.update({Instance.end_time: event.event_timestamp}).where(
            Instance.id.in_(instances),
        ).execute()
        self.context.ended_instances.extend(instances)

    def close_finished_instances(
        self, event: Event, instances: list[InstanceRef], journey_rules: Mapping[UUID, list[InstanceRule]]
    ) -> None:
        update_instances: list[UUID] = []
        for instance_ref in instances:
            # disable default end behavior if there are instance rules
            if instance_ref.journey in journey_rules:
                continue

            # Looking at a Journey's Pipelines, we can assess which Runs should exist within an Instance.
            # If every pipeline has at least one closed run for the current instance, it means the instance
            # is done and can be closed.
            closed_run_count = InstanceService.get_instance_run_counts(
                instance_ref.instance,
                exclude_run_statuses=(RunStatus.RUNNING.name, RunStatus.PENDING.name),
                journey=instance_ref.journey,
            )

            if all(closed_run_count.values()):
                update_instances.append(instance_ref.instance)
                LOG.info("Closing instance %s", instance_ref.instance)

        Instance.update({Instance.end_time: event.event_timestamp}).where(Instance.id.in_(update_instances)).execute()
        self.context.ended_instances.extend(update_instances)

    def default_instance_creation(self, event: Event) -> list[InstanceRef]:
        """
        Identify and return Instances associated with the given event.

        The precedence for identifying Instances are as follows.
        1. Instance that is already associated to the event's Run.
        2. Active Instance.
        3. Create a new Instance when the event's run does not exist OR when the run started in this context.
            - Cases where the event's run does not exist could be the event is not related to Batch Pipeline components,
            e.g. a DatasetOperationEvent, or a MessageLogEvent of a StreamingPipeline, etc.

        This evaluation is done once for each Journey where the event's Pipeline is
        included in the DAG. Associate the Run to the found Instance unless already
        done.
        """
        new_instances: list[Instance] = []
        identified_instances: list[InstanceRef] = []
        with_run = event.run_id is not None
        for journey in event.component_journeys:
            payload_keys: list[Optional[str]] = [None]
            if any(rule.action is InstanceRuleAction.END_PAYLOAD for rule in journey.instance_rules):
                payload_keys.extend(event.payload_keys)
            for payload_key in payload_keys:
                if (instance := _find_existing_instance(journey, with_run, payload_key)) is None:
                    instance = Instance(
                        journey=journey,
                        start_time=event.event_timestamp,
                        payload_key=payload_key,
                        start_type=InstanceStartType.PAYLOAD if payload_key else InstanceStartType.DEFAULT,
                    )
                    new_instances.append(instance)
                    LOG.info("Creating new instance: %s, payload key: %s", instance, payload_key)
                identified_instances.append(_make_instance_ref(instance))
        Instance.bulk_create(new_instances, batch_size=BATCH_SIZE)
        return identified_instances
