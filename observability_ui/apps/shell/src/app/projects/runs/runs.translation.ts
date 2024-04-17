import { MessageLogLevel } from '@observability-ui/core';

export const runsTranslation = {
  allTasks: 'All Tasks',
  noSelectedTask: 'Tasks',

  backToRuns: 'Back to Batch Runs',
  component_id: 'Component ID',

  graph: {
    errors: {
      renderingError: 'Unable to render the graph',
      action: 'Refresh',
    },
  },
  events: {
    logLevels: {
      [MessageLogLevel.Error]: 'Error',
      [MessageLogLevel.Warning]: 'Warning',
      [MessageLogLevel.Info]: 'Info',
    },
  },
  taskKey: 'Task Key',
  observedGraph: 'Observed Graph'
};
