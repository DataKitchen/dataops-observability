__all__ = ["EventService"]

from collections import defaultdict

from peewee import JOIN

from common.entities import (
    Component,
    EventEntity,
    Instance,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    Run,
    RunTask,
    Task,
)

from .helpers import ListRules, Page, ProjectEventFilters


class EventService:
    @staticmethod
    def get_events_with_rules(*, rules: ListRules, filters: ProjectEventFilters) -> Page[EventEntity]:
        """Query event storage according to the given filters"""
        if not filters:
            raise ValueError("Filter cannot be empty")

        query = EventEntity.select()
        for prefetch_entity in (Component, Run, Task, RunTask):
            query = (
                query.select_extend(prefetch_entity)
                .join(prefetch_entity, join_type=JOIN.LEFT_OUTER)
                .switch(EventEntity)
            )

        filter_list: list[object] = [EventEntity.project << filters.project_ids]

        if filters.instance_ids or filters.journey_ids:
            instance_set_subquery = InstanceSet.select(InstanceSet.id).join(InstancesInstanceSets).join(Instance)
            if filters.journey_ids:
                instance_set_subquery = instance_set_subquery.where(Instance.journey << filters.journey_ids)
            if filters.instance_ids:
                instance_set_subquery = instance_set_subquery.where(Instance.id << filters.instance_ids)
            query = query.where(EventEntity.instance_set.in_(instance_set_subquery))
        if filters.event_types:
            filter_list.append(EventEntity.type << filters.event_types)
        if filters.component_ids:
            filter_list.append(EventEntity.component << filters.component_ids)
        if filters.event_ids:
            filter_list.append(EventEntity.id << filters.event_ids)
        if filters.run_ids:
            filter_list.append(EventEntity.run << filters.run_ids)
        if filters.task_ids:
            filter_list.append(EventEntity.task << filters.task_ids)
        if filters.date_range_start:
            filter_list.append(EventEntity.timestamp >= filters.date_range_start)
        if filters.date_range_end:
            filter_list.append(EventEntity.timestamp < filters.date_range_end)

        query = query.where(*filter_list)
        page = Page[EventEntity].get_paginated_results(query, EventEntity.timestamp, rules)

        # Using a single query to fetch the Instance and Journey data
        instance_set_ids = {e.instance_set_id for e in page.results}
        instance_data = list(
            InstancesInstanceSets.select(InstancesInstanceSets.instance_set, Instance.id, Instance.journey)
            .join(Instance)
            .where(InstancesInstanceSets.instance_set << instance_set_ids)
            .tuples()
        )
        instance_data_dict = defaultdict(list)
        for instance_set_id, instance_id, journey_id in instance_data:
            instance_data_dict[instance_set_id].append(
                {"instance": Instance(id=instance_id), "journey": Journey(id=journey_id)}
            )
        for event in page.results:
            event.instances = instance_data_dict.get(event.instance_set_id, [])

        return page
