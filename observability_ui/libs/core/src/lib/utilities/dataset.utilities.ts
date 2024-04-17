import { DatasetOperationEventData, EventType, RunProcessedStatus, Schedule, TestStatus } from '../models';
import { getRunProcessedStatus, statusWeight } from './batch-runs.utilities';

export function getDatasetStatus(datasetOperationEvents: EventType[], tests: {
  status: TestStatus
}[], schedules: Schedule[]): RunProcessedStatus {
  const sortedTests = tests.map(t => t.status).sort((a, b) => statusWeight[b] - statusWeight[a]);

  // If at least 1 Failed or Warning, return Failed or Warning
  if (sortedTests.length > 0 && sortedTests[0] === TestStatus.Failed || sortedTests[0] === TestStatus.Warning) {
    return getRunProcessedStatus(sortedTests[0]);
  }

  // If expectations are set
  if (schedules.length > 0) {
    // If at least one write operation
    if (datasetOperationEvents.find(e => (e.raw_data as DatasetOperationEventData).operation === 'WRITE') !== undefined) {
      return RunProcessedStatus.Completed;
    } else {
      return RunProcessedStatus.Missing;
    }
  } else {
    // If expectation are not set
    // If at least one write operation
    if (datasetOperationEvents.find(e => (e.raw_data as DatasetOperationEventData).operation === 'WRITE') !== undefined) {
      return RunProcessedStatus.Completed;
    } else {
      return RunProcessedStatus.Pending;
    }
  }
}
