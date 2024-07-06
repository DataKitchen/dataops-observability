__all__ = ["RuleData"]

from typing import Optional
from uuid import UUID

from peewee import SelectQuery, fn

from common.entities import Run
from common.events.internal import RunAlert
from common.events.v1 import Event
from rules_engine.typing import EVENT_TYPE


class DatabaseData:
    """
    A class to provide database data to the rules engine
    """

    event: EVENT_TYPE

    def __init__(self, event: EVENT_TYPE) -> None:
        self.event = event

    def _get_batch_pipeline_id(self) -> Optional[UUID]:
        match self.event:
            case Event():
                return self.event.pipeline_id
            case RunAlert():
                return self.event.batch_pipeline_id
            case _:
                raise AttributeError("Unsupported event type")

    @property
    def runs(self) -> SelectQuery:
        """Returns query of runs matching event's pipeline orderd in descending start time"""
        if (pipeline_id := self._get_batch_pipeline_id()) is None:
            raise AttributeError("No pipeline id set in event")
        query: SelectQuery = (
            Run.select()
            .where(Run.pipeline == pipeline_id)
            .order_by(fn.COALESCE(Run.start_time, Run.expected_start_time).desc())
        )
        return query

    @property
    def runs_filter_name(self) -> SelectQuery:
        """Same as `runs` but filtered on run_name"""
        run_name_query = Run.select(Run.name).where(Run.id == getattr(self.event, "run_id"))
        return self.runs.where(Run.name.in_(run_name_query))


class RuleData:
    """
    A class wrapping data to be used in by rule evaluations

    Each class member create its own namespace of data that can be referenced when compiling rules.

    Examples:
    R(event__status__exact=RunStatus.COMPLETED)
    R(database__runs__exact=ALL(RunStatus.COMPLETED))
    """

    event: EVENT_TYPE
    database: DatabaseData

    def __init__(self, event: EVENT_TYPE) -> None:
        self.event = event
        self.database = DatabaseData(event)
