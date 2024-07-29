__all__ = ["InstanceDagService"]

from collections import defaultdict, Counter
from itertools import chain
from uuid import UUID

from peewee import JOIN, Case, fn, Value

from common.entities import (
    Component,
    DatasetOperation,
    DatasetOperationType,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstancesInstanceSets,
    InstanceSet,
    Run,
    RunStatus,
    Schedule,
    TestOutcome,
)
from common.entity_services.instance_service import ADDITIONAL_ALERT_DESCRIPTION, InstanceService
from common.events.v2.test_outcomes import TestStatus

RUN_STATUS_WEIGHT = {
  RunStatus.FAILED.value: 6,
  RunStatus.MISSING.value: 5,
  RunStatus.COMPLETED_WITH_WARNINGS.value: 4,
  RunStatus.RUNNING.value: 3,
  RunStatus.PENDING.value: 2,
  RunStatus.COMPLETED.value: 1,
  None: -1,
}


class InstanceDagService:
    @staticmethod
    def get_nodes_with_summaries(instance: Instance) -> dict[str, list]:
        nodes = []
        instance_dag = instance.journey_dag
        instance_dag_nodes = instance.dag_nodes

        statuses = InstanceDagService._get_nodes_status(instance, instance_dag_nodes)
        runs_summary = InstanceDagService._get_runs_summary(instance)
        tests_summary = InstanceDagService._get_tests_summary(instance)
        alerts_summary = InstanceDagService._get_alerts_summary(instance)
        operations_summary = InstanceDagService._get_operations_summary(instance)

        for component in instance_dag_nodes:
            nodes.append({
                "component": component,
                "edges": instance_dag[component],
                "status": statuses.get(component.id, RunStatus.PENDING.value),
                "runs_summary": runs_summary.get(component.id, []),
                "tests_summary": tests_summary.get(component.id, []),
                "alerts_summary": alerts_summary.get(component.id, []),
                "operations_summary": operations_summary.get(component.id, []),
            })
        return {"nodes": nodes}

    @staticmethod
    def _get_nodes_status(instance: Instance, nodes: list[Component]) -> dict[UUID, str]:
        runs_status_query = (
            Run.select(Run.pipeline, fn.COALESCE(Run.status, Value(RunStatus.PENDING.value)))
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .where(Run.pipeline << [component.id for component in nodes])
            .where(InstancesInstanceSets.instance == instance.id)
            .tuples()
        )
        datasets_status_query = (
            DatasetOperation.select(
                DatasetOperation.dataset,
                Case(
                    None,
                    (
                        (fn.SUM(fn.IF(DatasetOperation.operation == DatasetOperationType.WRITE.value, 1, 0)) > 0, Value(RunStatus.COMPLETED.value)),
                        ((fn.SUM(fn.IF(DatasetOperation.operation == DatasetOperationType.WRITE.value, 1, 0))) <= 0 & fn.SUM(fn.IF(Schedule.id != None, 1, 0)) > 0, Value(RunStatus.MISSING.value)),
                        ((fn.SUM(fn.IF(DatasetOperation.operation == DatasetOperationType.WRITE.value, 1, 0))) <= 0 & fn.SUM(fn.IF(Schedule.id != None, 1, 0)) <= 0, Value(RunStatus.PENDING.value)),
                    ),
                    Value(RunStatus.MISSING.value),
                ).alias("status"),
            )
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .join(Schedule, on=(Schedule.component == DatasetOperation.dataset), join_type=JOIN.LEFT_OUTER)
            .where(DatasetOperation.dataset << [component.id for component in nodes])
            .where(InstancesInstanceSets.instance == instance.id)
            .group_by(DatasetOperation.dataset)
            .tuples()
        )
        tests_status_query = (
            TestOutcome.select(
                TestOutcome.component,
                Case(
                    TestOutcome.status,
                    (
                        (Value(TestStatus.PASSED.value), Value(RunStatus.COMPLETED.value)),
                        (Value(TestStatus.WARNING.value), Value(RunStatus.COMPLETED_WITH_WARNINGS.value)),
                        (Value(TestStatus.FAILED.value), Value(RunStatus.FAILED.value)),
                    ),
                ),
            )
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .where(TestOutcome.component << [component.id for component in nodes])
            .where(InstancesInstanceSets.instance == instance.id)
            .tuples()
        )

        component_statuses: dict[str, str] = defaultdict(lambda: None)
        for component_id, status in chain(runs_status_query, datasets_status_query, tests_status_query):
            component_statuses[component_id] = max(
                component_statuses[component_id],
                status,
                key=lambda st: RUN_STATUS_WEIGHT[st],
            )
        return component_statuses

    @staticmethod
    def _get_runs_summary(instance: Instance) -> dict[UUID, list[dict]]:
        runs_summary_query = InstanceService.runs_summary_query([instance.id])
        runs_summary_query = (
            runs_summary_query.select(*runs_summary_query.selected_columns, Run.pipeline)
            .group_by(InstancesInstanceSets.instance, Run.pipeline, Run.status)
            .tuples()
        )

        runs_summary = defaultdict(list)
        for _, status, count, component_id in runs_summary_query:
            runs_summary[component_id].append({"status": status, "count": count})

        return runs_summary

    @staticmethod
    def _get_tests_summary(instance: Instance) -> dict[UUID, list[dict]]:
        tests_summary_query = InstanceService.tests_summary_query([instance.id])
        tests_summary_query = (
            tests_summary_query.select(*tests_summary_query.selected_columns, TestOutcome.component)
            .group_by(InstancesInstanceSets.instance, TestOutcome.component, TestOutcome.status)
            .tuples()
        )

        tests_summary = defaultdict(list)
        for _, status, count, component_id in tests_summary_query:
            tests_summary[component_id].append({"status": status, "count": count})

        return tests_summary

    @staticmethod
    def _get_alerts_summary(instance: Instance) -> dict[UUID, list[dict]]:
        instance_alerts_query = InstanceService.instance_alerts_query([instance])
        instance_alerts_query = (
            instance_alerts_query.select(
                *instance_alerts_query.selected_columns,
                InstanceAlertsComponents.component.alias("component_id"),
            )
            .join(InstanceAlertsComponents, on=(InstanceAlertsComponents.instance_alert == InstanceAlert.id))
        )

        run_alerts_query = InstanceService.run_alerts_query([instance])
        run_alerts_query = run_alerts_query.select(
            *run_alerts_query.selected_columns,
            Run.pipeline.alias("component_id"),
        )

        alerts = instance_alerts_query.union_all(run_alerts_query)
        agg_alerts = alerts.select_from(
            alerts.c.component_id,
            alerts.c.description,
            alerts.c.level,
            fn.COUNT(alerts.c.alert_id).alias("count"),
            fn.ROW_NUMBER()
                .over(partition_by=[alerts.c.component_id], order_by=[fn.COUNT(alerts.c.alert_id).desc()])
                .alias("row_num"),
        ).group_by(alerts.c.component_id, alerts.c.description, alerts.c.level)
        agg_data = list(agg_alerts)

        # top 10 alerts by count for each instance
        results = [
            {"component_id": UUID(a.component_id), "level": a.level, "description": a.description, "count": a.count}
            for a in agg_data
            if a.row_num <= 10
        ]
        if len(agg_data) > 10:
            additional_alerts_counter = Counter((UUID(a.component_id), a.level) for a in agg_data if a.row_num > 10)
            results.extend(
                [
                    {
                        "component_id": key[0],
                        "level": key[1],
                        "description": ADDITIONAL_ALERT_DESCRIPTION[key[1]],
                        "count": val,
                    }
                    for key, val in additional_alerts_counter.items()
                ]
            )
        alerts_summaries = defaultdict(list)
        for res in results:
            alerts_summaries[res["component_id"]].append(
                {"level": res["level"], "description": res["description"], "count": res["count"]}
            )

        return alerts_summaries

    @staticmethod
    def _get_operations_summary(instance: Instance) -> dict[UUID, list[dict]]:
        operations_summary_query = (
            DatasetOperation.select(
                InstancesInstanceSets.instance,
                DatasetOperation.dataset,
                DatasetOperation.operation,
                fn.COUNT(DatasetOperation.id).alias("count"),
            )
            .join(InstanceSet)
            .join(InstancesInstanceSets)
            .group_by(InstancesInstanceSets.instance, DatasetOperation.dataset, DatasetOperation.operation)
            .where(InstancesInstanceSets.instance == instance.id)
            .tuples()
        )

        operations_summary = defaultdict(list)
        for _, component_id, operation, count in operations_summary_query:
            operations_summary[component_id].append({"operation": operation, "count": count})

        return operations_summary
