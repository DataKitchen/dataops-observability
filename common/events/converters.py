from dataclasses import asdict, fields
from typing import cast

from common.entities import ComponentType, RunStatus
from common.entities.event import ApiEventType

from . import v1, v2
from .enums import EventSources
from .event_handler import EventHandlerBase
from .v1 import Event
from .v2.base import EventV2

# `Event` is not strictly ingested events but this is still the variables.utils intention
USER_EVENT_TYPES = Event | EventV2
"""Event types for ingested user events."""


class ConvertToV1(EventHandlerBase):
    v1_event: Event

    def _extract_common_attributes(self, event: EventV2) -> dict:
        return {
            "received_timestamp": event.created_timestamp,
            "event_timestamp": event.event_payload.event_timestamp,
            "external_url": event.event_payload.external_url,
            "metadata": event.event_payload.metadata,
            "version": event.version,
            "source": EventSources.API.name,
            "payload_keys": event.event_payload.payload_keys,
        }

    def _extract_batch_attributes(self, batch: v2.BatchPipelineData | None) -> dict:
        data = {
            "run_name": batch.run_name if batch else None,
            "run_key": batch.run_key if batch else None,
            "pipeline_key": batch.batch_key if batch else None,
            "pipeline_name": batch.details.name if batch and batch.details else None,
        }
        if batch and batch.details:
            data["component_tool"] = batch.details.tool
        return data

    def _extract_dataset_attributes(self, dataset: v2.DatasetData | None) -> dict:
        data = {
            "dataset_key": dataset.dataset_key if dataset else None,
            "dataset_name": dataset.details.name if dataset and dataset.details else None,
        }
        if dataset and dataset.details:
            data["component_tool"] = dataset.details.tool
        return data

    def _extract_server_attributes(self, server: v2.ServerData | None) -> dict:
        data = {
            "server_key": server.server_key if server else None,
            "server_name": server.details.name if server and server.details else None,
        }
        if server and server.details:
            data["component_tool"] = server.details.tool
        return data

    def _extract_stream_attributes(self, stream: v2.StreamData | None) -> dict:
        data = {
            "stream_key": stream.stream_key if stream else None,
            "stream_name": stream.details.name if stream and stream.details else None,
        }
        if stream and stream.details:
            data["component_tool"] = stream.details.tool
        return data

    def _extract_component_data(
        self,
        batch: v2.BatchPipelineData | None,
        dataset: v2.DatasetData | None,
        server: v2.ServerData | None,
        stream: v2.StreamData | None,
    ) -> dict:
        data = {
            **self._extract_batch_attributes(batch),
            **self._extract_dataset_attributes(dataset),
            **self._extract_server_attributes(server),
            **self._extract_stream_attributes(stream),
        }
        if "component_tool" not in data:
            data["component_tool"] = None
        return data

    def _extract_task_attributes(self, event: EventV2, batch: v2.BatchPipelineData | None) -> dict:
        return {
            "task_key": batch.task_key if batch else None,
            "task_name": batch.task_name if batch else None,
        }

    def _extract_id_attributes(self, event: EventV2) -> dict:
        return {
            "event_id": event.event_id,
            "project_id": event.project_id,
            "instances": event.instances,
            "run_id": event.run_id,
            "task_id": event.task_id,
            "run_task_id": event.run_task_id,
            "pipeline_id": event.component_id if event.component_type == ComponentType.BATCH_PIPELINE else None,
            "server_id": event.component_id if event.component_type == ComponentType.SERVER else None,
            "stream_id": event.component_id if event.component_type == ComponentType.STREAMING_PIPELINE else None,
            "dataset_id": event.component_id if event.component_type == ComponentType.DATASET else None,
        }

    def _extract_testgen_item_test_parameter(self, param: dict) -> v1.TestgenItemTestParameters:
        return v1.TestgenItemTestParameters(**param)

    def _extract_testgen_item(self, testgen: dict) -> v1.TestgenItem:
        return v1.TestgenItem(
            test_parameters=[
                self._extract_testgen_item_test_parameter(param) for param in testgen.pop("test_parameters")
            ],
            **testgen,
        )

    def _extract_test_outcome_item_integrations(
        self, integrations: dict | None
    ) -> v1.TestOutcomeItemIntegrations | None:
        if integrations is None:
            return None
        return v1.TestOutcomeItemIntegrations(testgen=self._extract_testgen_item(integrations["testgen"]))

    def _extract_test_outcomes(self, test_outcomes_v2: list[v2.TestOutcomeItem]) -> list[v1.TestOutcomeItem]:
        test_outcomes_v1 = []
        for outcome in test_outcomes_v2:
            outcome_dict = asdict(outcome)
            outcome_dict["status"] = outcome.status.name
            outcome_dict["min_threshold"] = outcome_dict.pop("metric_min_threshold", None)
            outcome_dict["max_threshold"] = outcome_dict.pop("metric_max_threshold", None)
            outcome_dict["integrations"] = self._extract_test_outcome_item_integrations(
                outcome_dict.pop("integrations", None)
            )

            test_outcomes_v1.append(v1.TestOutcomeItem(**outcome_dict))
        return test_outcomes_v1

    def _extract_testgen_table(self, tables: dict) -> v1.TestgenTable:
        return v1.TestgenTable(
            **tables,
        )

    def _extract_testgen_table_group_config(
        self, table_group_configuration: dict | None
    ) -> v1.TestgenTableGroupV1 | None:
        if table_group_configuration is None:
            return None
        return v1.TestgenTableGroupV1(
            **table_group_configuration,
        )

    def _extract_testgen_integrations(self, testgen: dict) -> v1.TestgenDataset:
        return v1.TestgenDataset(
            version=v1.TestgenIntegrationVersions[testgen.pop("version").name],
            tables=self._extract_testgen_table(testgen.pop("tables")),
            table_group_configuration=self._extract_testgen_table_group_config(
                testgen.pop("table_group_configuration")
            ),
            **testgen,
        )

    def _extract_testgen_integration_componenet(self, integrations: dict) -> v1.TestGenTestOutcomeIntegrations:
        return v1.TestGenTestOutcomeIntegrations(
            testgen=self._extract_testgen_integrations(integrations["testgen"]),
        )

    def _extract_component_integrations(
        self, component: v2.TestGenComponentData
    ) -> v1.TestGenTestOutcomeIntegrationComponent | None:
        integrations = next(c for f in fields(component) if (c := getattr(component, f.name, None))).integrations
        if integrations is None:
            return None
        return v1.TestGenTestOutcomeIntegrationComponent(
            integrations=self._extract_testgen_integration_componenet(asdict(integrations)),
        )

    def handle_run_status(self, event: v1.RunStatusEvent) -> bool:
        self.v1_event = event
        return True

    def handle_message_log(self, event: v1.MessageLogEvent) -> bool:
        self.v1_event = event
        return True

    def handle_metric_log(self, event: v1.MetricLogEvent) -> bool:
        self.v1_event = event
        return True

    def handle_test_outcomes(self, event: v1.TestOutcomesEvent) -> bool:
        self.v1_event = event
        return True

    def handle_dataset_operation(self, event: v1.DatasetOperationEvent) -> bool:
        self.v1_event = event
        return True

    def handle_batch_pipeline_status_user_v2(self, event: v2.BatchPipelineStatusUserEvent) -> bool:
        payload = event.event_payload
        self.v1_event = v1.RunStatusEvent(
            status=payload.status.name,
            event_type=v1.RunStatusEvent.__name__,
            **self._extract_common_attributes(event),
            **self._extract_component_data(
                batch=payload.batch_pipeline_component, dataset=None, server=None, stream=None
            ),
            **self._extract_task_attributes(event, payload.batch_pipeline_component),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_dataset_operation_v2(self, event: v2.DatasetOperationUserEvent) -> bool:
        payload = event.event_payload
        self.v1_event = v1.DatasetOperationEvent(
            operation=payload.operation.name,
            path=payload.path,
            event_type=v1.DatasetOperationEvent.__name__,
            **self._extract_common_attributes(event),
            **self._extract_component_data(batch=None, dataset=payload.dataset_component, server=None, stream=None),
            **self._extract_task_attributes(event, None),
            **self._extract_id_attributes(event),
        )
        return True

    # N.B: A ingested v2 MessageLog/MetricLog event cannot be converted to a v1 event since it may contain several
    # entries. The v1 event equivalents do not support multiple entries. This limiation is fine since the plan is to
    # only convert ingested v1 events.
    def handle_message_log_v2(self, event: v2.MessageLogUserEvent) -> bool:
        payload = event.event_payload
        message = payload.log_entries[0]
        self.v1_event = v1.MessageLogEvent(
            log_level=message.level.name,
            message=message.message,
            event_type=v1.MessageLogEvent.__name__,
            **self._extract_common_attributes(event),
            **self._extract_component_data(
                batch=payload.component.batch_pipeline,
                dataset=payload.component.dataset,
                server=payload.component.server,
                stream=payload.component.stream,
            ),
            **self._extract_task_attributes(event, payload.component.batch_pipeline),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_metric_log_v2(self, event: v2.MetricLogUserEvent) -> bool:
        payload = event.event_payload
        metric = payload.metric_entries[0]
        self.v1_event = v1.MetricLogEvent(
            metric_key=metric.key,
            metric_value=metric.value,
            event_type=v1.MetricLogEvent.__name__,
            **self._extract_common_attributes(event),
            **self._extract_component_data(
                batch=payload.component.batch_pipeline,
                dataset=payload.component.dataset,
                server=payload.component.server,
                stream=payload.component.stream,
            ),
            **self._extract_task_attributes(event, payload.component.batch_pipeline),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_test_outcomes_v2(self, event: v2.TestOutcomesUserEvent) -> bool:
        payload = event.event_payload
        self.v1_event = v1.TestOutcomesEvent(
            test_outcomes=self._extract_test_outcomes(payload.test_outcomes),
            component_integrations=self._extract_component_integrations(payload.component),
            event_type=v1.TestOutcomesEvent.__name__,
            **self._extract_common_attributes(event),
            **self._extract_component_data(
                batch=payload.component.batch_pipeline,
                dataset=payload.component.dataset,
                server=payload.component.server,
                stream=payload.component.stream,
            ),
            **self._extract_task_attributes(event, payload.component.batch_pipeline),
            **self._extract_id_attributes(event),
        )
        return True


class ConvertToV2(EventHandlerBase):
    v2_event: EventV2

    def _extract_common_payload_attributes(self, event: Event) -> dict:
        return {
            "event_timestamp": event.event_timestamp,
            "external_url": event.external_url,
            "metadata": event.metadata,
            "payload_keys": event.payload_keys,
        }

    def _extract_common_internal_attributes(self, event: Event) -> dict:
        return {
            "created_timestamp": event.received_timestamp,
            "component_type": event.component_type,
            "version": event.version,
        }

    def _extract_batch_pipeline_data(self, event: Event) -> v2.BatchPipelineData | None:
        new_component_data = (
            v2.NewComponentData(name=event.pipeline_name, tool=event.component_tool)
            if event.pipeline_name or event.component_tool
            else None
        )
        if event.pipeline_key and event.run_key:
            return v2.BatchPipelineData(
                batch_key=event.pipeline_key,
                run_key=event.run_key,
                run_name=event.run_name,
                details=new_component_data,
                task_key=getattr(event, "task_key", None),
                task_name=getattr(event, "task_name", None),
            )
        else:
            return None

    def _extract_testgen_batch_pipeline_data(self, event: v1.TestOutcomesEvent) -> v2.TestGenBatchPipelineData | None:
        if data := self._extract_batch_pipeline_data(event):
            return v2.TestGenBatchPipelineData(
                batch_key=data.batch_key,
                run_key=data.run_key,
                run_name=data.run_name,
                details=data.details,
                task_key=data.task_key,
                task_name=data.task_name,
                integrations=self._extract_testgen_integration_componenet(event),
            )
        return None

    def _extract_testgen_dataset_data(self, event: v1.TestOutcomesEvent) -> v2.TestGenDatasetData | None:
        if data := self._extract_dataset_data(event):
            return v2.TestGenDatasetData(
                dataset_key=data.dataset_key,
                details=data.details,
                integrations=self._extract_testgen_integration_componenet(event),
            )
        return None

    def _extract_testgen_stream_data(self, event: v1.TestOutcomesEvent) -> v2.TestGenStreamData | None:
        if data := self._extract_stream_data(event):
            return v2.TestGenStreamData(
                stream_key=data.stream_key,
                details=data.details,
                integrations=self._extract_testgen_integration_componenet(event),
            )
        return None

    def _extract_testgen_server_data(self, event: v1.TestOutcomesEvent) -> v2.TestGenServerData | None:
        if data := self._extract_server_data(event):
            return v2.TestGenServerData(
                server_key=data.server_key,
                details=data.details,
                integrations=self._extract_testgen_integration_componenet(event),
            )
        return None

    def _extract_dataset_data(self, event: Event) -> v2.DatasetData | None:
        new_component_data = (
            v2.NewComponentData(name=event.dataset_name, tool=event.component_tool)
            if event.dataset_name or event.component_tool
            else None
        )
        if event.dataset_key:
            return v2.DatasetData(dataset_key=event.dataset_key, details=new_component_data)
        else:
            return None

    def _extract_stream_data(self, event: Event) -> v2.StreamData | None:
        new_component_data = (
            v2.NewComponentData(name=event.stream_name, tool=event.component_tool)
            if event.stream_name or event.component_tool
            else None
        )
        if event.stream_key:
            return v2.StreamData(
                stream_key=event.stream_key,
                details=new_component_data,
            )
        else:
            return None

    def _extract_server_data(self, event: Event) -> v2.ServerData | None:
        new_component_data = (
            v2.NewComponentData(name=event.server_name, tool=event.component_tool)
            if event.server_name or event.component_tool
            else None
        )
        if event.server_key:
            return v2.ServerData(
                server_key=event.server_key,
                details=new_component_data,
            )
        else:
            return None

    def _extract_id_attributes(self, event: Event) -> dict:
        return {
            "event_id": event.event_id,
            "project_id": event.project_id,
            "instances": event.instances,
            "run_id": event.run_id,
            "task_id": event.task_id,
            "run_task_id": event.run_task_id,
            "component_id": event.component_id,
        }

    def _extract_component_data(self, event: Event) -> v2.ComponentData:
        return v2.ComponentData(
            batch_pipeline=self._extract_batch_pipeline_data(event),
            dataset=self._extract_dataset_data(event),
            server=self._extract_server_data(event),
            stream=self._extract_stream_data(event),
        )

    def _extract_testgen_component_data(self, event: v1.TestOutcomesEvent) -> v2.TestGenComponentData:
        return v2.TestGenComponentData(
            batch_pipeline=self._extract_testgen_batch_pipeline_data(event),
            dataset=self._extract_testgen_dataset_data(event),
            server=self._extract_testgen_server_data(event),
            stream=self._extract_testgen_stream_data(event),
        )

    def _extract_testgen_item_test_parameter(self, param: dict) -> v2.TestgenItemTestParameters:
        return v2.TestgenItemTestParameters(**param)

    def _extract_testgen_item(self, testgen: dict) -> v2.TestgenItem:
        return v2.TestgenItem(
            test_parameters=[
                self._extract_testgen_item_test_parameter(param) for param in testgen.pop("test_parameters")
            ],
            **testgen,
        )

    def _extract_test_outcome_item_integrations(
        self, integrations: dict | None
    ) -> v2.TestOutcomeItemIntegrations | None:
        if integrations is None:
            return None
        return v2.TestOutcomeItemIntegrations(testgen=self._extract_testgen_item(integrations["testgen"]))

    def _extract_test_outcomes(self, test_outcomes_v1: list[v1.TestOutcomeItem]) -> list[v2.TestOutcomeItem]:
        test_outcomes_v2 = []
        for outcome in test_outcomes_v1:
            outcome_dict = asdict(outcome)
            outcome_dict["status"] = v2.TestStatus[outcome.status]
            outcome_dict["metric_min_threshold"] = outcome_dict.pop("min_threshold", None)
            outcome_dict["metric_max_threshold"] = outcome_dict.pop("max_threshold", None)
            outcome_dict["integrations"] = self._extract_test_outcome_item_integrations(
                outcome_dict.pop("integrations", None)
            )

            test_outcomes_v2.append(v2.TestOutcomeItem(**outcome_dict))
        return test_outcomes_v2

    def _extract_testgen_table(self, tables: dict) -> v2.TestgenTable:
        return v2.TestgenTable(
            **tables,
        )

    def _extract_testgen_table_group_config(
        self, table_group_configuration: dict | None
    ) -> v2.TestgenTableGroupV1 | None:
        if table_group_configuration is None:
            return None
        return v2.TestgenTableGroupV1(
            **table_group_configuration,
        )

    def _extract_testgen_integrations(self, testgen: dict) -> v2.TestgenDataset:
        return v2.TestgenDataset(
            version=v2.TestgenIntegrationVersions[testgen.pop("version").name],
            tables=self._extract_testgen_table(testgen.pop("tables")),
            table_group_configuration=self._extract_testgen_table_group_config(
                testgen.pop("table_group_configuration")
            ),
            **testgen,
        )

    def _extract_testgen_integration_componenet(
        self, event: v1.TestOutcomesEvent
    ) -> v2.TestGenTestOutcomeIntegrations | None:
        if i := event.component_integrations:
            return v2.TestGenTestOutcomeIntegrations(
                testgen=self._extract_testgen_integrations(asdict(i.integrations.testgen)),
            )
        else:
            return None

    def handle_run_status(self, event: v1.RunStatusEvent) -> bool:
        self.v2_event = v2.BatchPipelineStatusUserEvent(
            event_payload=v2.BatchPipelineStatus(
                status=RunStatus[event.status],
                # Cast because run status always has batch pipeline data
                batch_pipeline_component=cast(v2.BatchPipelineData, self._extract_batch_pipeline_data(event)),
                **self._extract_common_payload_attributes(event),
            ),
            event_type=ApiEventType.BATCH_PIPELINE_STATUS,
            **self._extract_common_internal_attributes(event),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_message_log(self, event: v1.MessageLogEvent) -> bool:
        self.v2_event = v2.MessageLogUserEvent(
            event_payload=v2.MessageLog(
                log_entries=[v2.LogEntry(level=v2.LogLevel[event.log_level], message=event.message)],
                component=self._extract_component_data(event),
                **self._extract_common_payload_attributes(event),
            ),
            event_type=ApiEventType.MESSAGE_LOG,
            **self._extract_common_internal_attributes(event),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_metric_log(self, event: v1.MetricLogEvent) -> bool:
        self.v2_event = v2.MetricLogUserEvent(
            event_payload=v2.MetricLog(
                metric_entries=[v2.MetricEntry(key=event.metric_key, value=event.metric_value)],
                component=self._extract_component_data(event),
                **self._extract_common_payload_attributes(event),
            ),
            event_type=ApiEventType.METRIC_LOG,
            **self._extract_common_internal_attributes(event),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_test_outcomes(self, event: v1.TestOutcomesEvent) -> bool:
        self.v2_event = v2.TestOutcomesUserEvent(
            event_payload=v2.TestOutcomes(
                test_outcomes=self._extract_test_outcomes(event.test_outcomes),
                component=self._extract_testgen_component_data(event),
                **self._extract_common_payload_attributes(event),
            ),
            event_type=ApiEventType.TEST_OUTCOMES,
            **self._extract_common_internal_attributes(event),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_dataset_operation(self, event: v1.DatasetOperationEvent) -> bool:
        self.v2_event = v2.DatasetOperationUserEvent(
            event_payload=v2.DatasetOperation(
                operation=v2.DatasetOperationType[event.operation],
                path=event.path,
                # Cast because run status always has batch pipeline data
                dataset_component=cast(v2.DatasetData, self._extract_dataset_data(event)),
                **self._extract_common_payload_attributes(event),
            ),
            event_type=ApiEventType.DATASET_OPERATION,
            **self._extract_common_internal_attributes(event),
            **self._extract_id_attributes(event),
        )
        return True

    def handle_batch_pipeline_status_user_v2(self, event: v2.BatchPipelineStatusUserEvent) -> bool:
        self.v2_event = event
        return True

    def handle_dataset_operation_v2(self, event: v2.DatasetOperationUserEvent) -> bool:
        self.v2_event = event
        return True

    def handle_message_log_v2(self, event: v2.MessageLogUserEvent) -> bool:
        self.v2_event = event
        return True

    def handle_metric_log_v2(self, event: v2.MetricLogUserEvent) -> bool:
        self.v2_event = event
        return True

    def handle_test_outcomes_v2(self, event: v2.TestOutcomesUserEvent) -> bool:
        self.v2_event = event
        return True


def to_v1(event: USER_EVENT_TYPES) -> Event:
    converter = ConvertToV1()
    event.accept(converter)
    return converter.v1_event


def to_v2(event: USER_EVENT_TYPES) -> EventV2:
    converter = ConvertToV2()
    event.accept(converter)
    return converter.v2_event
