__all__ = ["TestOutcomeService"]

from typing import Optional
from uuid import UUID

from peewee import SqliteDatabase

from common.constants.peewee import BATCH_SIZE
from common.entities import DB, TestgenDatasetComponent, TestGenTestOutcomeIntegration, TestOutcome
from common.events.v1.test_outcomes_event import TestgenDataset, TestOutcomesEvent
from common.predicate_engine.query import getattr_recursive


class TestOutcomeService:
    @staticmethod
    def insert_from_event(
        *,
        event: TestOutcomesEvent,
        component_id: UUID,
        instance_set_id: Optional[UUID] = None,
        run_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
    ) -> None:
        test_outcomes = []
        test_outcome_integrations = []
        # Noted TestOutcomesEvent (hence TestOutcomeItem(s)) is already validated in the run_manager
        for t in event.test_outcomes:
            # Per pd-1091, default start_time to the event time and end_time to start_time
            start_time = t.start_time if t.start_time else event.event_timestamp
            end_time = t.end_time if t.end_time else start_time
            test_outcome = TestOutcome(
                key=t.key,
                result=t.result,
                type=t.type,
                dimensions=t.dimensions if t.dimensions else [],
                metric_name=t.metric_name,
                metric_description=t.metric_description,
                name=t.name,
                description=t.description,
                status=t.status,
                metric_value=t.metric_value,
                min_threshold=t.min_threshold,
                max_threshold=t.max_threshold,
                start_time=start_time,
                end_time=end_time,
                run_id=run_id,
                task_id=task_id,
                component=component_id,
                instance_set=instance_set_id,
                external_url=event.external_url,
            )
            test_outcomes.append(test_outcome)

            if (integrations := t.integrations) is not None:
                if (testgen_item := integrations.testgen) is not None:
                    test_outcome_integrations.append(
                        TestGenTestOutcomeIntegration(
                            table=testgen_item.table,
                            columns=testgen_item.columns,
                            test_suite=testgen_item.test_suite,
                            version=testgen_item.version,
                            test_parameters=[x.json_dict for x in testgen_item.test_parameters],
                            test_outcome=test_outcome,
                        )
                    )

        # Using the recursive lookup avoids having to check for None on optional values up the whole chain
        testgen_dataset: Optional[TestgenDataset] = getattr_recursive(
            event, "component_integrations__integrations__testgen", None
        )

        with DB.atomic():
            if testgen_dataset is not None:
                table_group_config = testgen_dataset.table_group_configuration
                testgen_dataset_data = {
                    "database_name": testgen_dataset.database_name,
                    "connection_name": testgen_dataset.database_name,
                    "schema": testgen_dataset.schema,
                    "table_list": testgen_dataset.tables.include_list,
                    "table_include_pattern": testgen_dataset.tables.include_pattern,
                    "table_exclude_pattern": testgen_dataset.tables.exclude_pattern,
                    "table_group_id": table_group_config.group_id if table_group_config else None,
                    "project_code": table_group_config.project_code if table_group_config else None,
                    "uses_sampling": True if table_group_config and table_group_config.uses_sampling else False,
                    "sample_percentage": table_group_config.sample_percentage if table_group_config else None,
                    "sample_minimum_count": table_group_config.sample_minimum_count if table_group_config else None,
                }
                conflict_kwargs: dict[str, object] = {"update": testgen_dataset_data}
                if isinstance(DB.obj, SqliteDatabase):  # Sqlite requires setting a conflict_target
                    conflict_kwargs["conflict_target"] = [TestgenDatasetComponent.component]

                TestgenDatasetComponent.insert(
                    {**testgen_dataset_data, **{"component": component_id}},
                ).on_conflict(**conflict_kwargs).execute()
            TestOutcome.bulk_create(test_outcomes, batch_size=BATCH_SIZE)
            TestGenTestOutcomeIntegration.bulk_create(test_outcome_integrations, batch_size=BATCH_SIZE)
