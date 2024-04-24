import { getCompleteSummary } from './task-test-summary.utils';
import { RunProcessedStatus, TestStatus } from '@observability-ui/core';

describe('task-test-summary.utils', () => {

  describe('#getCompleteSummary', () => {

    it('should be defensive', () => {

      const expected = {TOTAL: 0};

      expect(getCompleteSummary()).toEqual(expected);
      expect(getCompleteSummary([])).toEqual(expected);
      expect(getCompleteSummary(undefined)).toEqual(expected);
    });

    it('should parse a list of task summaries and count the total', () => {

      expect(getCompleteSummary([
        { status: RunProcessedStatus.Running.toString(), count: 3 },
        { status: RunProcessedStatus.CompletedWithWarnings.toString(), count: 0 },
        { status: RunProcessedStatus.Pending.toString(), count: 12 },
        { status: RunProcessedStatus.Missing.toString(), count: 1 },
        { status: RunProcessedStatus.Failed.toString(), count: 2 },
        { status: RunProcessedStatus.Completed.toString(), count: 7 },
      ])).toEqual({
        [RunProcessedStatus.Running]: 3,
        [RunProcessedStatus.CompletedWithWarnings]: 0,
        [RunProcessedStatus.Pending]: 12,
        [RunProcessedStatus.Missing]: 1,
        [RunProcessedStatus.Failed]: 2,
        [RunProcessedStatus.Completed]: 7,
        TOTAL: 25,
      });

    });

    it('should parse a list of tests summaries and count the total', () => {

      expect(getCompleteSummary([
        { status: TestStatus.Failed, count: 3 },
        { status: TestStatus.Passed, count: 10, },
        { status: TestStatus.Warning, count: 2 },
        { status: TestStatus.Warning, count: 3 },
        { status: TestStatus.Passed, count: 1 },
      ])).toEqual({
        [TestStatus.Failed]: 3,
        [TestStatus.Passed]: 11,
        [TestStatus.Warning]: 5,
        TOTAL: 19,
      });

    });
  });
});
