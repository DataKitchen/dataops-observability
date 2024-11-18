__all__ = ["ComponentService"]

from datetime import datetime
from itertools import cycle
from typing import Optional
from collections.abc import Generator

from peewee import Select

from common.constants import BATCH_SIZE
from common.entities import Component, Instance, Journey, JourneyDagEdge


class ComponentService:
    @staticmethod
    def select_journeys(component: Component) -> Select:
        """
        Generates a query that finds Journeys that contains a given component.
        """
        journeys = (
            Journey.select()
            .join(JourneyDagEdge)
            .join(
                Component,
                on=(JourneyDagEdge.right == Component.id) | (JourneyDagEdge.left == Component.id),
            )
            .where(Component.id == component.id)
            .distinct()
        )
        return journeys

    @classmethod
    def get_or_create_active_instances(
        cls, component: Component, start_time: Optional[datetime] = None
    ) -> Generator[tuple[bool, Instance], None, None]:
        """
        Retrieves active Instances for a given component. Create active Instances when a Journey does not have one.

        Returns a generator of 2-tuples where the first item is a boolean flag indicating when the Instance was
        created and the second item is the Instance object.
        """
        new_instances: list[Instance] = []
        start_time = start_time or datetime.utcnow()
        for journey in cls.select_journeys(component).prefetch(Instance.select().where(Instance.active == True)):
            yield from zip(cycle((False,)), journey.instances)
            if not journey.instances:
                new_instances.append(Instance(journey=journey, start_time=start_time))

        Instance.bulk_create(new_instances, batch_size=BATCH_SIZE)
        yield from zip(cycle((True,)), new_instances)
