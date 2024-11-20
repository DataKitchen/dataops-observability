__all__ = ["ProjectService"]

from functools import reduce
from operator import or_
from typing import Any, Optional

from peewee import PREFETCH_TYPE, Value, fn, prefetch, DoesNotExist

from common.entities import (
    Action,
    Company,
    Component,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceAlertType,
    InstanceRule,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Organization,
    Pipeline,
    Project,
    Run,
    RunAlert,
    RunAlertType,
    RunTask,
    Schedule,
    TestgenDatasetComponent,
    TestOutcome,
    ActionImpl,
)
from common.entity_services.upcoming_instance_service import UpcomingInstanceService
from observability_api.schemas.alert_schemas import UIAlertSchema

from .helpers import (
    AlertFilters,
    ComponentFilters,
    Filters,
    ListRules,
    Page,
    RunFilters,
    SortOrder,
    TestOutcomeItemFilters,
)
from .instance_service import InstanceService
from ..actions.action import BaseAction
from ..actions.action_factory import action_factory
from ..exceptions.service import MultipleActionsFound


class ProjectService:
    @staticmethod
    def get_test_outcomes_with_rules(
        project: Project, rules: ListRules, filters: TestOutcomeItemFilters
    ) -> Page[TestOutcome]:
        query = TestOutcome.select(TestOutcome).where(TestOutcome.component.in_(project.components))
        if rules.search is not None:
            query = query.where(
                ((TestOutcome.name ** f"%{rules.search}%") | (TestOutcome.description ** f"%{rules.search}%"))
            )
        if filters:
            if statuses := filters.statuses:
                query = query.where(TestOutcome.status.in_(statuses))
            if component_ids := filters.component_ids:
                query = query.where(TestOutcome.component << component_ids)
            if start_range_begin := filters.start_range_begin:
                query = query.where(TestOutcome.start_time >= start_range_begin)
            if start_range_end := filters.start_range_end:
                query = query.where(TestOutcome.start_time < start_range_end)
            if end_range_begin := filters.end_range_begin:
                query = query.where(TestOutcome.end_time >= end_range_begin)
            if end_range_end := filters.end_range_end:
                query = query.where(TestOutcome.end_time < end_range_end)
            if run_ids := filters.run_ids:
                query = query.where(TestOutcome.run.in_(run_ids))
            if instance_ids := filters.instance_ids:
                instance_set_subquery = (
                    InstanceSet.select(InstanceSet.id)
                    .join(InstancesInstanceSets)
                    .where(InstancesInstanceSets.instance.in_(instance_ids))
                )
                query = query.where(TestOutcome.instance_set.in_(instance_set_subquery))
            if key := filters.key:
                query = query.where(TestOutcome.key == key)

        return Page[TestOutcome].get_paginated_results(query, TestOutcome.start_time, rules)

    @staticmethod
    def get_components_with_rules(project_id: str, rules: ListRules, filters: ComponentFilters) -> Page[Component]:
        base_query = Component.project == project_id
        if rules.search is not None:
            base_query &= (Component.key ** f"%{rules.search}%") | (Component.name ** f"%{rules.search}%")
        if filters.component_types:
            base_query &= Component.type.in_(filters.component_types)
        if filters.tools:
            base_query &= Component.tool.in_(filters.tools)
        query = Component.select().where(base_query)
        # Used coalesce to avoid having null name records first
        paginated_query = query.order_by(
            rules.order_by_field(fn.coalesce(fn.nullif(Component.name, ""), Component.key)),
            rules.order_by_field(Component.key),
        ).paginate(rules.page, rules.count)
        prefetched_query = prefetch(paginated_query, TestgenDatasetComponent, prefetch_type=PREFETCH_TYPE.JOIN)
        return Page[Component](results=list(prefetched_query), total=query.count())

    @staticmethod
    def get_runs_with_rules(
        project_id: Optional[str], pipeline_ids: list[str], rules: ListRules, filters: RunFilters
    ) -> Page[Run]:
        start_dt = fn.COALESCE(Run.start_time, Run.expected_start_time)
        query = Run.select(Run, start_dt.alias("start_dt")).distinct()
        memberships = []
        if pipeline_ids or project_id or (filters and filters.pipeline_keys):
            query = query.join(Pipeline).switch(Run)
        if project_id is not None:
            memberships.append(Pipeline.project == project_id)
        if pipeline_ids:
            memberships.append(Pipeline.id.in_(pipeline_ids))
        if rules.search is not None:
            memberships.append((Run.key ** f"%{rules.search}%") | (Run.name ** f"%{rules.search}%"))
        if filters:
            if filters.statuses:
                memberships.append(Run.status.in_(filters.statuses))
            if filters.run_keys:
                memberships.append(Run.key.in_(filters.run_keys))
            if filters.pipeline_keys:
                memberships.append(Pipeline.key.in_(filters.pipeline_keys))
            if filters.start_range_begin:
                memberships.append(Run.start_time >= filters.start_range_begin)
            if filters.start_range_end:
                memberships.append(Run.start_time < filters.start_range_end)
            if filters.end_range_begin:
                memberships.append(Run.end_time >= filters.end_range_begin)
            if filters.end_range_end:
                memberships.append(Run.end_time < filters.end_range_end)
            if filters.instance_ids:
                query = query.join(InstanceSet).join(InstancesInstanceSets).switch(Run)
                memberships.append(InstancesInstanceSets.instance.in_(filters.instance_ids))
            if filters.tools:
                memberships.append(Pipeline.tool.in_(filters.tools))

        query = query.where(*memberships)
        paginated_query = query.order_by(rules.order_by_field(start_dt)).paginate(rules.page, rules.count)
        tasks_summary = RunTask.select(RunTask.run, RunTask.status, fn.COUNT(RunTask.id).alias("count")).group_by(
            RunTask.run, RunTask.status
        )
        tests_summary = TestOutcome.select(
            TestOutcome.run, TestOutcome.status, fn.COUNT(TestOutcome.id).alias("count")
        ).group_by(TestOutcome.run, TestOutcome.status)
        result = paginated_query.prefetch(tasks_summary, tests_summary, prefetch_type=PREFETCH_TYPE.JOIN)
        return Page[Run](results=result, total=query.count())

    @staticmethod
    def get_instances_with_rules(
        rules: ListRules, filters: Filters, project_ids: list[str], company_id: Optional[str] = None
    ) -> Page[Instance]:
        memberships = [Journey.project.in_(project_ids)] if project_ids else []
        if company_id:
            memberships.append(Company.id == company_id)
        if rules.search is not None:
            memberships.append(Instance.payload_key ** f"%{rules.search}%")
        if filters:
            if filters.journey_ids:
                memberships.append(Journey.id.in_(filters.journey_ids))
            if filters.journey_names:
                memberships.append(Journey.name.in_(filters.journey_names))
            if filters.active is True or filters.active is False:
                memberships.append(Instance.active == filters.active)
            if filters.start_range_begin:
                memberships.append(Instance.start_time >= filters.start_range_begin)
            if filters.start_range_end:
                memberships.append(Instance.start_time < filters.start_range_end)
            if filters.end_range_begin:
                memberships.append(Instance.end_time >= filters.end_range_begin)
            if filters.end_range_end:
                memberships.append(Instance.end_time < filters.end_range_end)
            if filters.statuses and (status_filter := Instance.make_status_filter(filters.statuses)):
                memberships.append(reduce(or_, status_filter))

        query = (
            Instance.select(Instance, Journey, Project)
            .join(Journey)
            .join(Project)
            .join(Organization)
            .join(Company)
            .where(*memberships)
        )

        results = (
            query.order_by(rules.order_by_field(Instance.start_time))
            .paginate(rules.page, rules.count)
            .prefetch(Journey, InstanceRule, Component, Schedule, prefetch_type=PREFETCH_TYPE.JOIN)
        )

        for instance in results:
            if (
                instance.active
                and (
                    upcoming := next(
                        UpcomingInstanceService.get_upcoming_instances(instance.journey, instance.start_time), None
                    )
                )
                is not None
            ):
                instance.expected_end_time = upcoming.expected_start_time or upcoming.expected_end_time
        InstanceService.aggregate_runs_summary(results)
        InstanceService.aggregate_tests_summary(results)
        InstanceService.aggregate_alerts_summary(results)
        return Page[Instance](results=results, total=query.count())

    @staticmethod
    def get_journeys_with_rules(project_id: str, rules: ListRules, component_id: Optional[str] = None) -> Page[Journey]:
        base_query = Journey.project == project_id
        if rules.search is not None:
            base_query &= Journey.name ** f"%{rules.search}%"
        if component_id:
            query = (
                Journey.select()
                .join(
                    JourneyDagEdge, on=((JourneyDagEdge.left == component_id) | (JourneyDagEdge.right == component_id))
                )
                .switch(Journey)
                .where((Journey.id == JourneyDagEdge.journey) & base_query)
                .distinct()
            )
        else:
            query = Journey.select().where(base_query)

        results = (
            query.order_by(rules.order_by_field(Journey.name))
            .paginate(rules.page, rules.count)
            .prefetch(InstanceRule, prefetch_type=PREFETCH_TYPE.JOIN)
        )
        return Page[Journey](results=results, total=query.count())

    @staticmethod
    def get_alerts_with_rules(project_id: str, rules: ListRules, filters: AlertFilters) -> Page[dict[str, Any]]:
        run_alerts_clause = [Project.id == project_id]
        instance_alerts_clause = [Project.id == project_id]
        if rules.search is not None:
            instance_alerts_clause.append(InstanceAlert.description ** f"%{rules.search}%")
            run_alerts_clause.append(RunAlert.description ** f"%{rules.search}%")
        if filters:
            if filters.date_range_start:
                instance_alerts_clause.append(InstanceAlert.created_on >= filters.date_range_start)
                run_alerts_clause.append(RunAlert.created_on >= filters.date_range_start)
            if filters.date_range_end:
                instance_alerts_clause.append(InstanceAlert.created_on < filters.date_range_end)
                run_alerts_clause.append(RunAlert.created_on < filters.date_range_end)
            if filters.levels:
                instance_alerts_clause.append(InstanceAlert.level.in_(filters.levels))
                run_alerts_clause.append(RunAlert.level.in_(filters.levels))
            if filters.component_ids:
                instance_alerts_clause.append(InstanceAlertsComponents.component.in_(filters.component_ids))
                run_alerts_clause.append(Run.pipeline.in_(filters.component_ids))
            if filters.instance_ids:
                instance_alerts_clause.append(Instance.id.in_(filters.instance_ids))
                run_alerts_clause.append(Instance.id.in_(filters.instance_ids))
            if filters.run_ids:
                # default false for instance alerts
                instance_alerts_clause.append(InstanceAlert.id.is_null())
                run_alerts_clause.append(Run.id.in_(filters.run_ids))
            if filters.run_keys:
                # default false for instance alerts
                instance_alerts_clause.append(InstanceAlert.id.is_null())
                run_alerts_clause.append(Run.key.in_(filters.run_keys))
            if filters.types:
                instance_alerts_clause.append(
                    InstanceAlert.type.in_([t for t in filters.types if t in InstanceAlertType.__members__])
                )
                run_alerts_clause.append(RunAlert.type.in_([t for t in filters.types if t in RunAlertType.__members__]))
        alerts_union = (
            InstanceAlert.select(
                InstanceAlert.id.alias("instance_id"),
                Value(None).alias("run_id"),
                InstanceAlert.created_on,
            )
            .distinct()
            .left_outer_join(InstanceAlertsComponents)
            .switch(InstanceAlert)
            .join(Instance)
            .join(Journey)
            .join(Project)
            .where(*instance_alerts_clause)
        ).union_all(
            RunAlert.select(
                Value(None).alias("instance_id"),
                RunAlert.id.alias("run_id"),
                RunAlert.created_on,
            )
            .join(Run)
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .join(Instance)
            .join(Journey)
            .join(Project)
            .where(*run_alerts_clause)
        )
        alerts = alerts_union.select_from(
            alerts_union.c.instance_id,
            alerts_union.c.run_id,
            alerts_union.c.created_on,
        )

        ordering = rules.order_by_field(alerts_union.c.created_on)
        paginated = list(alerts.order_by(ordering).paginate(rules.page, rules.count))
        instance_alerts = (
            InstanceAlert.select(InstanceAlert).where(
                InstanceAlert.id.in_([a.instance_id for a in paginated if a.instance_id])
            )
        ).prefetch(InstanceAlertsComponents, Component)
        run_alerts = list(
            RunAlert.select(RunAlert, Run).join(Run).where(RunAlert.id.in_([a.run_id for a in paginated if a.run_id]))
        )

        combined_alerts = run_alerts + instance_alerts
        combined_alerts.sort(
            key=lambda a: a.created_on,
            reverse=True if rules.sort == SortOrder.DESC else False,
        )
        return Page(results=UIAlertSchema().dump(combined_alerts, many=True), total=alerts.count())

    @staticmethod
    def get_template_actions(project: Project, actions: list[ActionImpl]) -> dict[str, Action]:
        template_actions = {}
        template_actions_query = (
            Action.select()
            .join(Company)
            .join(Organization)
            .join(Project)
            .where(Project.id == project.id, Action.action_impl.in_(actions))
        )
        try:
            for ta in template_actions_query:
                if ta.action_impl.name in template_actions:
                    raise MultipleActionsFound(
                        f"Expected 0..1 template action for {ta.action_impl.name} but found multiple"
                    )
                template_actions[ta.action_impl.name] = ta
        except DoesNotExist:
            pass
        return template_actions

    @classmethod
    def get_alert_actions(cls, project: Project) -> list[BaseAction]:
        """Initializes the Action classes required by a project alerts configuration."""
        if not project.alert_actions:
            return []

        template_actions = cls.get_template_actions(project, [pa["action_impl"] for pa in project.alert_actions])
        actions = []
        for action in project.alert_actions:
            actions.append(
                action_factory(
                    action["action_impl"], action["action_args"], template_actions.get(action["action_impl"], None)
                )
            )
        return actions
