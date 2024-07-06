import logging
from dataclasses import asdict

from common.entities import Journey, JourneyDagEdge
from common.events.internal import InstanceAlert, RunAlert
from common.events.v1 import Event
from rules_engine.typing import EVENT_TYPE, Rule
from rules_engine.journey_rules import get_rules

LOG = logging.getLogger(__name__)


def evaluate_rules(event: EVENT_TYPE, *rules: Rule) -> None:
    """Evaluate all the rules for a given event."""
    total = len(rules)
    LOG.info("Found %s rule(s) to evaluate", total)
    padding = len(str(total))  # Used in progress indicator

    for idx, rule in enumerate(rules, start=1):
        LOG.info("[#m<%s/%s>] Evaluating: %s", str(idx).zfill(padding), total, rule)
        rule.evaluate(event)


def process_v1_event(event: Event) -> None:
    LOG.info("Processing %s Event", event.__class__.__name__, extra={"event": asdict(event)})
    if not event.component_id:
        LOG.warning("Event %s is missing the required attribute `component_id`.", event)
        return

    rules = get_rules(*(r.journey for r in event.instances))
    evaluate_rules(event, *rules)


def process_instance_alert(event: InstanceAlert) -> None:
    """Evaluate rules for internal InstanceAlert events."""
    LOG.info("Processing internal InstanceAlert event", extra={"event": asdict(event)})
    if (journey_id := event.journey_id) is None:
        LOG.warning("InstanceAlert has no `journey_id`; no rules to evaluate.")
    else:
        rules = get_rules(journey_id)
        evaluate_rules(event, *rules)


def process_run_alert(event: RunAlert) -> None:
    """Evaluate rules for internal RunAlert events."""
    LOG.info("Processing internal RunAlert event", extra={"event": asdict(event)})
    if (pipeline_id := event.batch_pipeline_id) is None:
        LOG.info("RunAlert has no `batch_pipeline_id`; no rules to evaluate")
    else:
        journeys = (
            Journey.select()
            .join(JourneyDagEdge, on=((JourneyDagEdge.left == pipeline_id) | (JourneyDagEdge.right == pipeline_id)))
            .switch(Journey)
            .where(Journey.id == JourneyDagEdge.journey)
            .distinct()
        )
        rules = get_rules(*[j.id for j in journeys])
        evaluate_rules(event, *rules)
