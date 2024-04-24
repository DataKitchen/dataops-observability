import { EventType, RunProcessedStatus, Schedule, TestStatus } from '../models';
import { getDatasetStatus } from './dataset.utilities';

describe('getDatasetStatus', () => {
  it('should return Failed if at least one test is Failed', () => {
    const datasetOperationEvents: EventType[] = [
      {
        raw_data: {
          operation: 'WRITE'
        }
      } as EventType
    ];

    const tests: { status: TestStatus }[] = [
      { status: TestStatus.Failed }
    ];

    const schedules: Schedule[] = [];

    expect(getDatasetStatus(datasetOperationEvents, tests, schedules)).toEqual(RunProcessedStatus.Failed);
  });

  it('should return CompletedWithWarnings if at least one test is Warning', () => {
    const datasetOperationEvents: EventType[] = [
      {
        raw_data: {
          operation: 'WRITE'
        }
      } as EventType
    ];

    const tests: { status: TestStatus }[] = [
      { status: TestStatus.Warning }
    ];

    const schedules: Schedule[] = [];

    expect(getDatasetStatus(datasetOperationEvents, tests, schedules)).toEqual(RunProcessedStatus.CompletedWithWarnings);
  });

  describe('if there are no Failed or Warning tests and there is at least one schedule', () => {
    it('should return completed if there is at least one WRITE operation', () => {
      const datasetOperationEvents: EventType[] = [
        {
          raw_data: {
            operation: 'WRITE'
          }
        } as EventType
      ];
      const tests: { status: TestStatus }[] = [ { status: TestStatus.Passed } ];
      const schedules: Schedule[] = [ {} as Schedule ];

      expect(getDatasetStatus(datasetOperationEvents, tests, schedules)).toEqual(RunProcessedStatus.Completed);
    });

    it('should return missing if there are no WRITE operations', () => {
      const datasetOperationEvents: EventType[] = [
        {
          raw_data: {
            operation: 'READ'
          }
        } as EventType
      ];
      const tests: { status: TestStatus }[] = [ { status: TestStatus.Passed } ];
      const schedules: Schedule[] = [ {} as Schedule ];

      expect(getDatasetStatus(datasetOperationEvents, tests, schedules)).toEqual(RunProcessedStatus.Missing);
    });
  });

  describe('if there are no Failed or Warning tests and there are no schedules', () => {
    it('should return completed if there is at least one WRITE operation', () => {
      const datasetOperationEvents: EventType[] = [
        {
          raw_data: {
            operation: 'WRITE'
          }
        } as EventType
      ];
      const tests: { status: TestStatus }[] = [ { status: TestStatus.Passed } ];
      const schedules: Schedule[] = [];

      expect(getDatasetStatus(datasetOperationEvents, tests, schedules)).toEqual(RunProcessedStatus.Completed);
    });

    it('should return pending if there are no WRITE operations', () => {
      const datasetOperationEvents: EventType[] = [
        {
          raw_data: {
            operation: 'READ'
          }
        } as EventType
      ];
      const tests: { status: TestStatus }[] = [ { status: TestStatus.Passed } ];
      const schedules: Schedule[] = [];

      expect(getDatasetStatus(datasetOperationEvents, tests, schedules)).toEqual(RunProcessedStatus.Pending);
    });
  });
});
