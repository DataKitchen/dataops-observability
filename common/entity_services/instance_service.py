__all__ = ["InstanceService"]

from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID

from peewee import ModelSelect, Value, fn

from common.entities import (
    AlertLevel,
    Instance,
    InstanceAlert,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Run,
    RunAlert,
    TestOutcome,
)

ADDITIONAL_ALERT_DESCRIPTION = {
    AlertLevel.ERROR.value: "Additional Errors (ct)",
    AlertLevel.WARNING.value: "Additional Warnings (ct)",
}


class InstanceService:
    @staticmethod
    def aggregate_runs_summary(instances: Iterable[Instance]) -> None:
        runs_summary_dict = defaultdict(list)
        for inst, status, count in InstanceService.runs_summary_query([inst.id for inst in instances]).tuples():
            runs_summary_dict[inst].append({"status": status, "count": count})

        for instance in instances:
            instance.runs_summary = runs_summary_dict[instance.id]

    @staticmethod
    def runs_summary_query(ids: Iterable[UUID]) -> ModelSelect:
        return (
            Run.select(InstancesInstanceSets.instance, Run.status, fn.COUNT(Run.id).alias("count"))
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .group_by(InstancesInstanceSets.instance, Run.status)
            .where(InstancesInstanceSets.instance << ids)
        )

    @staticmethod
    def aggregate_tests_summary(instances: Iterable[Instance]) -> None:
        tests_summary_dict = defaultdict(list)
        for inst, status, count in InstanceService.tests_summary_query([inst.id for inst in instances]).tuples():
            tests_summary_dict[inst].append({"status": status, "count": count})

        for instance in instances:
            instance.tests_summary = tests_summary_dict[instance.id]

    @staticmethod
    def tests_summary_query(ids: Iterable[UUID]) -> ModelSelect:
        return (
            TestOutcome.select(
                InstancesInstanceSets.instance, TestOutcome.status, fn.COUNT(TestOutcome.id).alias("count")
            )
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .group_by(InstancesInstanceSets.instance, TestOutcome.status)
            .where(InstancesInstanceSets.instance << ids)
            .tuples()
        )

    @staticmethod
    def aggregate_alerts_summary(instances: Iterable[Instance]) -> None:
        instance_alerts = InstanceService.instance_alerts_query(instances)
        run_alerts = InstanceService.run_alerts_query(instances)

        # Query all instance alerts and run alerts of the specified instances
        alerts = instance_alerts.union_all(run_alerts)
        # Aggregate alerts by description and level for each instance
        agg_alerts = alerts.select_from(
            alerts.c.instance_id,
            alerts.c.description,
            alerts.c.level,
            fn.COUNT(alerts.c.alert_id).alias("count"),
            fn.ROW_NUMBER()
            .over(partition_by=[alerts.c.instance_id], order_by=[fn.COUNT(alerts.c.alert_id).desc()])
            .alias("row_num"),
        ).group_by(alerts.c.instance_id, alerts.c.description, alerts.c.level)
        agg_data = list(agg_alerts)
        # top 10 alerts by count for each instance
        results = [
            {"instance_id": UUID(a.instance_id), "level": a.level, "description": a.description, "count": a.count}
            for a in agg_data
            if a.row_num <= 10
        ]
        if len(agg_data) > 10:
            additional_alerts_counter = Counter((UUID(a.instance_id), a.level) for a in agg_data if a.row_num > 10)
            results.extend(
                [
                    {
                        "instance_id": key[0],
                        "level": key[1],
                        "description": ADDITIONAL_ALERT_DESCRIPTION[key[1]],
                        "count": val,
                    }
                    for key, val in additional_alerts_counter.items()
                ]
            )
        alerts_summaries = defaultdict(list)
        for res in results:
            alerts_summaries[res["instance_id"]].append(
                {"level": res["level"], "description": res["description"], "count": res["count"]}
            )
        for instance in instances:
            instance.alerts_summary = sorted(
                alerts_summaries[instance.id],
                key=lambda k: (
                    1 if k["description"] not in ADDITIONAL_ALERT_DESCRIPTION.values() else 2,
                    -k["count"],
                    k["description"],
                ),
            )

    @staticmethod
    def instance_alerts_query(instances: Iterable[Instance]) -> ModelSelect:
        return (
            InstanceAlert.select(
                InstanceAlert.id.alias("alert_id"),
                InstanceAlert.description.alias("description"),
                InstanceAlert.level.alias("level"),
                Instance.id.alias("instance_id"),
                Journey.id,
                Journey.project,
            )
            .join(Instance)
            .join(Journey)
            # Additional filter by journey id to help query performance
            .where((Instance.id.in_(instances)) & (Journey.id.in_([i.journey.id for i in instances])))
        )

    @staticmethod
    def run_alerts_query(instances: Iterable[Instance]) -> ModelSelect:
        return (
            RunAlert.select(
                RunAlert.id.alias("alert_id"),
                RunAlert.description.alias("description"),
                RunAlert.level.alias("level"),
                Instance.id.alias("instance_id"),
                Journey.id,
                Journey.project,
            )
            .join(Run)
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .join(Instance)
            .join(Journey)
            # Additional filter by journey id to help query performance
            .where((Instance.id.in_(instances)) & (Journey.id.in_([i.journey.id for i in instances])))
        )

    @staticmethod
    def get_instance_run_counts(
        instance: UUID | Instance,
        *,
        include_run_statuses: Optional[Iterable[str]] = None,
        exclude_run_statuses: Optional[Iterable[str]] = None,
        journey: Optional[UUID] = None,
        pipelines: Optional[Iterable[UUID]] = None,
        end_before: Optional[datetime] = None,
    ) -> dict[UUID, int]:
        """
        Return a dict of pipelines with the corresponding run count per pipeline.
        If parameter pipelines is not provided, return all pipelines expected in the instance's journey.

        * Runs with status present in parameter include_run_statuses are included in the count.
        * Runs with status present in parameter exclude_run_statuses are excluded from the count.
        * Exclude parameters include_run_statuses and exclude_run_statuses to disable the status checks
        """

        if journey is None:
            journey_in = Journey.select().join(Instance).where(Instance.id == instance)
        else:
            journey_in = (journey,)

        memberships_all = [JourneyDagEdge.journey.in_(journey_in)]
        memberships_count = [InstancesInstanceSets.instance == instance]
        if pipelines:
            memberships_all.append(Pipeline.id.in_(pipelines))
            memberships_count.append(Run.pipeline.in_(pipelines))
        run_counts = dict(
            Pipeline.select(Pipeline.id, Value(0))
            .join(JourneyDagEdge, on=(JourneyDagEdge.right == Pipeline.id) | (JourneyDagEdge.left == Pipeline.id))
            .where(*memberships_all)
            .tuples()
        )

        if include_run_statuses is not None:
            memberships_count.append(Run.status.in_(include_run_statuses))
        if exclude_run_statuses:
            memberships_count.append(Run.status.not_in(exclude_run_statuses))
        if end_before:
            memberships_count.append(Run.end_time < end_before)

        run_counts.update(
            Run.select(Run.pipeline, fn.COUNT(Run.id))
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .where(*memberships_count)
            .group_by(Run.pipeline)
            .tuples()
        )
        return run_counts
