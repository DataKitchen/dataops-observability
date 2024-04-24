import { EventTypes, InstanceStatus, RunProcessedStatus, TestStatus } from '@observability-ui/core';

export const coreTranslations = {

  name: 'name',
  description: 'description',

  save: 'save',
  cancel: 'cancel',


  event: 'event',
  events: 'Events',
  allEvents: 'All Events',

  eventType: 'Event Type',
  eventTypes: 'Event Types',
  allEventTypes: 'All Event Types',

  component: 'Component',
  componentKey: 'Component Key',
  components: 'Components',
  allComponents: 'All Components',

  journey: 'journey',

  status: 'Status',
  allStatuses: 'All Statuses',

  batchRuns: 'Batch Runs',
  timeline: 'Timeline',

  timestamp: 'Timestamp',
  eventOrTask: 'Event/Task',
  details: 'Details',

  [EventTypes.MessageLogEvent]: 'Message Log',
  [EventTypes.MetricLogEvent]: 'Metric Log',
  [EventTypes.TestOutcomesEvent]: 'Test Outcomes',
  [EventTypes.RunStatusEvent]: 'Run Status',
  [EventTypes.DatasetOperationEvent]: 'Dataset Operation',

  graph: 'graph',
  rule: 'rule',
  rules: 'rules',
  run: 'run',
  task: 'task',
  tasks: 'tasks',
  test: 'test',
  tests: 'tests',

  user: 'user',

  active: 'active',
  actions: 'actions',

  selectAll: 'Select All',
  searchOptions: 'Search Options',

  edit: 'edit',
  settings: 'Settings',

  testStatus: {
    [TestStatus.Passed]: 'Passed',
    [TestStatus.Failed]: 'Failed',
    [TestStatus.Warning]: 'Warning',
  },

  // standalone component do not support .forChild operator on translation module
  // we need to review why that is and move this on metric-log-rule.component.ts
  exact: 'equals',
  // not_equal: 'not equals',
  lt: 'less than',
  lte: 'less than or equals',
  gt: 'greater than',
  gte: 'greater than or equals',
  ERROR: 'Error',
  WARNING: 'Warning',
  INFO: 'Info',

  RUNNING: 'Running',
  COMPLETED: 'Completed',

  runStatus: {
    [RunProcessedStatus.Running]: 'Running',
    [RunProcessedStatus.Failed]: 'Failed',
    [RunProcessedStatus.Completed]: 'Completed',
    [RunProcessedStatus.Missing]: 'Missing',
    [RunProcessedStatus.Pending]: 'Pending',
    [RunProcessedStatus.CompletedWithWarnings]: 'Completed With Warnings',

    STARTED: 'Running',
    ERROR: 'Failed',
  },

  instanceStatus: {
    [InstanceStatus.Active]: 'Active',
    [InstanceStatus.Error]: 'Error',
    [InstanceStatus.Warning]: 'Warning',
    [InstanceStatus.Completed]: 'Completed',
    [InstanceStatus.Upcoming]: 'Upcoming',
  },

  // TODO move this stuff in a better place since they are part of a standalone component
  code: 'Code',
  copy: 'Copy',
  copied: 'Copied'
};
