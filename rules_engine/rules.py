from __future__ import annotations

__all__ = ["get_global_rules", "get_rules", "register_global_rule", "Rule"]

import logging
import time
from functools import lru_cache
from threading import local
from typing import Any, Callable, Optional
from uuid import UUID

from common.entities import Rule as RuleEntity
from common.entity_services import JourneyService
from common.events.internal import RunAlert
from common.events.v1 import Event
from common.predicate_engine.compilers import compile_schema
from common.predicate_engine.query import R
from common.predicate_engine.schemas.simple_v1 import RuleDataSchema
from conf import settings
from rules_engine import EVENT_TYPE
from rules_engine.actions import ActionResult, action_factory
from rules_engine.rule_data import RuleData

LOG = logging.getLogger(__name__)

_rule_local = local()
"""Object for storing globally registered rules."""


class Rule:
    """A rule definition. Takes an R object for rules evaluation and a list of callables to trigger for matches."""

    __slots__ = ("journey_id", "r_obj", "rule_entity", "component_id", "triggers")

    def __init__(
        self,
        r_obj: R,
        rule_entity: RuleEntity,
        *triggers: Callable,
        journey_id: Optional[UUID] = None,
        component_id: Optional[UUID] = None,
    ) -> None:
        self.r_obj: R = r_obj
        self.rule_entity = rule_entity
        self.triggers: tuple[Callable[[EVENT_TYPE, RuleEntity, Optional[UUID]], ActionResult], ...] = triggers
        self.journey_id: Optional[UUID] = journey_id
        self.component_id: Optional[UUID] = component_id

    @staticmethod
    def _get_component_id(event: EVENT_TYPE) -> Optional[UUID]:
        """Extract the component id from the given event."""
        match event:
            case Event():
                return event.component_id
            case RunAlert():
                return event.batch_pipeline_id
            case _:
                return None

    def evaluate(self, event: EVENT_TYPE) -> None:
        LOG.info("Evaluating event: %s", event)
        if (component_id := self._get_component_id(event)) is not None:
            if self.component_id is not None and component_id != self.component_id:
                LOG.debug(
                    "RESULT: False - This Rule does not apply to Component: `%s`, event: `%s`",
                    self.component_id,
                    event,
                )
                return None

        if self.r_obj.matches(RuleData(event)):
            LOG.info("RESULT: True: `%s` matches event: `%s`", self.r_obj, event)
            for trigger in self.triggers:
                LOG.debug("Running trigger `%s` for event `%s`", trigger, event)
                try:
                    trigger(event, self.rule_entity, self.journey_id)
                except Exception:
                    LOG.exception("Error running trigger `%s` with event `%s`", trigger, event)
        else:
            LOG.debug("RESULT: False: `%s` does not match event: `%s`", self.r_obj, event)

    def __str__(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}: {self.r_obj}"

    def register(self) -> None:
        """Manually register the current rule instance."""
        if (registered_rules := getattr(_rule_local, "registered_rules", None)) is None:
            _rule_local.registered_rules = []
            registered_rules = _rule_local.registered_rules
        registered_rules.append(self)


def register_global_rule(rule: Rule) -> None:
    """Manually register a global rule."""
    if (registered_rules := getattr(_rule_local, "registered_rules", None)) is None:
        _rule_local.registered_rules = []
        registered_rules = _rule_local.registered_rules
    if rule not in registered_rules:
        registered_rules.append(rule)


def get_global_rules() -> tuple[Rule, ...]:
    """Return a tuple of globally registered rules."""
    try:
        return tuple(_rule_local.registered_rules)
    except AttributeError:
        LOG.debug("No global rules found.")
        return ()


def _execute_action(event: EVENT_TYPE, rule_entity: RuleEntity, journey_id: Optional[UUID]) -> Any:
    action_entity = JourneyService.get_action_by_implementation(rule_entity.journey_id, rule_entity.action)
    action = action_factory(rule_entity, action_entity)
    action.execute(event, rule_entity, journey_id)


@lru_cache(maxsize=50)
def _get_rules(journey_ids: frozenset[UUID], _ttl: int) -> list[Rule]:
    # Makes linter not implode
    del _ttl

    rules: list[Rule] = []
    # Add any globally registered rules
    rules.extend(get_global_rules())

    rule_entities = RuleEntity.select(RuleEntity).where(RuleEntity.journey.in_(journey_ids))
    for rule_entity in rule_entities:
        try:
            parsed_rule_data = RuleDataSchema().load(rule_entity.rule_data)
            rule_obj = compile_schema(rule_entity.rule_schema, parsed_rule_data)
            r = Rule(
                rule_obj,
                rule_entity,
                _execute_action,
                journey_id=rule_entity.journey_id,
                component_id=rule_entity.component_id,
            )
            rules.append(r)
        except Exception:
            # TODO: Don't catch all exceptions since the users won't have great visibility over what's wrong
            LOG.exception("Exception setting up rule evaluator for rule %s", rule_entity.id)
    return rules


def get_rules(*journey_ids: UUID) -> list[Rule]:
    """
    Return a list of Rule objects. Uses _get_rules for LRU cache.

    This finds and returns all rules that exist for a given component_id value as well as any rules that have been
    globally registered.

    TODO: Future changes to the Events V2 will allow us to leverage an instance ID or Journey ID to acquire rules.
    """
    _ttl = round(time.time() / settings.RULE_REFRESH_SECONDS)
    return _get_rules(frozenset(journey_ids), _ttl)
