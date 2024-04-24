import { WithId } from '../entity';
import { ComponentType, ShortComponent } from './component.model';
import { TestgenTestOutcomeIntegrationV1 } from './integrations.model';
import { RunProcessedStatus } from './runs.model';

interface ComponentDetails {
  name?: string;
  tool?: string;
}

interface BatchPipelineComponent {
  batch_key: string;
  details?: ComponentDetails;
  run_key: string;
  run_name?: string;
  task_key?: string;
  task_name?: string;
}
interface DatasetComponent {
  dataset_key: string;
  details?: ComponentDetails;
}
interface ServerComponent {
  server_key: string;
  details?: ComponentDetails;
}
interface StreamComponent {
  stream_key: string;
  details?: ComponentDetails;
}

interface EventComponent {
  batch_pipeline?: BatchPipelineComponent;
  dataset?: DatasetComponent;
  server?: ServerComponent;
  stream?: StreamComponent;
}
export interface EventData {
  event_timestamp?: string;
  external_url?: string;
  metadata?: unknown;
  payload_keys?: string[];
}

export interface MessageLogEventData extends EventData {
  component: EventComponent;
  log_entries: Array<{
    level: MessageLogLevel;
    message: string;
  }>;
}

export enum MessageLogLevel {
  Error = 'ERROR',
  Warning = 'WARNING',
  Info = 'INFO',
}

export interface MetricLogEventData extends EventData {
  component: EventComponent;
  metric_entries: Array<{
    key: string;
    value: string;
  }>; 
}

export interface RunStatusEventData extends EventData {
  batch_pipeline_component: BatchPipelineComponent;
  status: RunProcessedStatus;
}

export interface TestOutcomesEventData extends EventData {
  component: EventComponent;
  test_outcomes: TestOutcomeItem[];
}

export interface DatasetOperationEventData extends EventData {
  dataset_component: DatasetComponent;
  path: string;
  operation: 'READ' | 'WRITE';
}

export interface TestOutcomeItem {
  id: string;
  name: string;
  status: TestStatus;
  description: string;

  key?: string;
  type?: string;
  result?: string;
  dimensions?: string[];
  start_time?: string;
  end_time?: string;

  metric_name?: string;
  metric_description?: string;
  metric_value?: number;
  min_threshold?: number;
  max_threshold?: number;

  component?: { id: string; display_name: string; type: ComponentType };
  integrations?: TestgenTestOutcomeIntegrationV1[];

  metadata?: unknown;
  external_url?: string;
}


export enum TestStatus {
  Passed = 'PASSED',
  Failed = 'FAILED',
  Warning = 'WARNING',
}

export interface EventType {
  id: string;
  event_type: EventTypes;
  timestamp: string;
  project?: WithId;
  instances: Array<{ instance: WithId; journey: WithId }>;
  components: ShortComponent[];
  component_key?: string;
  run?: WithId;
  task?: WithId;
  task_key?: string;
  run_task?: WithId;

  raw_data: EventData | MessageLogEventData |
    MetricLogEventData |
    RunStatusEventData |
    TestOutcomesEventData |
    DatasetOperationEventData;

  // leaving it optional so in mocked data we do not need to specify it
  version?: 1 | 2;
}


export enum EventTypes {
  MessageLogEvent = 'MESSAGE_LOG',
  MetricLogEvent = 'METRIC_LOG',
  RunStatusEvent = 'BATCH_PIPELINE_STATUS',
  TestOutcomesEvent = 'TEST_OUTCOMES',
  DatasetOperationEvent = 'DATASET_OPERATION',
}

export interface EventSearchFields {
  journey_id?: string;
  component_id?: string;
  run_id?: string;
  instance_id?: string;
  task_id?: string;
  date_range_start?: string;
  date_range_end?: string;
  event_type?: string;
  component_name?: string;
}
