import { EventType, EventTypes, MessageLogLevel, RunProcessedStatus, TestStatus } from '@observability-ui/core';

const mockMessageLogEvent: EventType = {
  instances: [],
  components: [],
  raw_data: {
    component: {
      batch_pipeline: {
        batch_key: 'my-pipeline',
        details: {
          name: 'my-pipeline',
        },
        run_key: 'my-run',
      },
    },
    log_entries: [{
      message: 'my log message',
      level: MessageLogLevel.Error,
    }],
  },
  timestamp: new Date().toISOString(),
  id: '1',
  event_type: EventTypes.MessageLogEvent,
};

const mockMetricLogEvent: EventType = {
  instances: [],
  components: [],
  raw_data: {
    component: {
      batch_pipeline: {
        batch_key: 'my-pipeline',
        details: {
          name: 'my-pipeline',
        },
        run_key: 'my-run',
      },
    },
    metric_entries: [{
      key: 'metric-key',
      value: '10',
    }],
  },
  timestamp: new Date().toISOString(),
  id: '1',
  event_type: EventTypes.MetricLogEvent,
};

const mockRunStatusEvent: EventType = {
  instances: [],
  components: [],
  raw_data: {
    metadata: {},
    batch_pipeline_component: {
      batch_key: 'my-pipeline',
      details: {
        name: 'my-pipeline',
      },
      run_key: 'my-run',
    },
    status: RunProcessedStatus.Completed,
  },
  timestamp: new Date().toISOString(),
  id: '1',
  event_type: EventTypes.RunStatusEvent,
};

const mockRunStatusEventWithTaskName: EventType = {
  instances: [],
  components: [],
  raw_data: {
    batch_pipeline_component: {
      batch_key: 'my-pipeline',
      details: {
        name: 'my-pipeline',
      },
      run_key: 'my-run',
      task_key: 'my-task',
      task_name: 'my-task',
    },
    status: RunProcessedStatus.Running,
  },
  timestamp: new Date().toISOString(),
  id: '1',
  event_type: EventTypes.RunStatusEvent,
};

const mockTestOutcomesEvent: EventType = {
  instances: [],
  components: [],
  raw_data: {
    component: {
      batch_pipeline: {
        batch_key: 'my-pipeline',
        details: {
          name: 'my-pipeline',
        },
        run_key: 'my-run',
      }
    },
    test_outcomes: [
      {
        id: 'test-1',
        description: 'first-test',
        metadata: {},
        status: TestStatus.Passed,
        name: 'test-1'
      },
      {
        id: 'test-2',
        description: 'first-test',
        metadata: {},
        status: TestStatus.Passed,
        name: 'test-2'
      },
      {
        id: 'test-3',
        description: 'first-test',
        metadata: {},
        status: TestStatus.Passed,
        name: 'test-3'
      },
      {
        id: 'test-f-1',
        description: 'first-test',
        metadata: {},
        status: TestStatus.Failed,
        name: 'test-f-1'
      },
      {
        id: 'test-f-2',
        description: 'first-test',
        metadata: {},
        status: TestStatus.Failed,
        name: 'test-f-2'
      },
      {
        id: 'test-w-1',
        description: 'first-test',
        metadata: {},
        status: TestStatus.Warning,
        name: 'test-w-1'
      }
    ]
  },
  timestamp: new Date().toISOString(),
  id: '1',
  event_type: EventTypes.TestOutcomesEvent,
};

export const mockRunEvents = [
  mockMessageLogEvent,
  mockMetricLogEvent,
  mockRunStatusEvent,
  mockRunStatusEventWithTaskName,
  mockTestOutcomesEvent,
];
