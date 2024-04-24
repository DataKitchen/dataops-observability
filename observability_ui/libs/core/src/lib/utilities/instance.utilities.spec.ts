import { aggregateAlerts, parseInstances, testsByComponent } from './instance.utilities';
import { Instance, InstanceRunSummary, TestOutcomeItem, TestStatus } from '../models';

describe('instance.utilities', () => {
  describe('aggregateAlerts()', () => {
    const alerts = [
      { level: 'ERROR', message: 'Error 1', count: 1 },
      { level: 'ERROR', message: 'Error 2', count: 1 },
      { level: 'ERROR', description: 'Error 3', count: 1 },
      { level: 'WARNING', message: 'Warning 1', count: 1 }
    ] as any;

    it('should count the error alerts', () => {
      expect(aggregateAlerts(alerts)).toEqual(expect.objectContaining({ errors: expect.objectContaining({ count: 3 }) }));
    });

    it('should add all the error alerts in an array', () => {
      expect(aggregateAlerts(alerts)).toEqual(expect.objectContaining({ errors: expect.objectContaining({ alerts: alerts.filter((a: any) => a.level === 'ERROR') }) }));
    });

    it('should count the warning alerts', () => {
      expect(aggregateAlerts(alerts)).toEqual(expect.objectContaining({ warnings: expect.objectContaining({ count: 1 }) }));
    });

    it('should add all the warning alerts in an array', () => {
      expect(aggregateAlerts(alerts)).toEqual(expect.objectContaining({ warnings: expect.objectContaining({ alerts: alerts.filter((a: any) => a.level === 'WARNING') }) }));
    });
  });

  describe('testByComponents', () => {
    it('should group tests by component', () => {
      const tests: TestOutcomeItem[] = [
        {
          status: TestStatus.Failed,
          component: {
            display_name: 'test',
            id: 'id1'
          },
        } as TestOutcomeItem,
        {
          status: TestStatus.Passed,
          component: {
            display_name: 'test2',
            id: 'id2'
          },
        } as TestOutcomeItem
      ];

      const expected = {
          id1: [
            {
              'component': {
                'display_name': 'test',
                'id': 'id1',
              },
              'status': 'FAILED',
            },
          ],
          id2:
            [
              {
                'component': {
                  'display_name': 'test2',
                  'id': 'id2',
                },
                'status': 'PASSED',
              },
            ]
        }
      ;

      expect(testsByComponent(tests)).toEqual(expected);
    });
  });

  describe('parseInstances', () => {

    it('should parse an instance', () => {

      const now = new Date();
      const startTime = new Date();
      startTime.setHours(0);
      startTime.setMinutes(0);
      startTime.setSeconds(0);
      expect(parseInstances({
        start_time: new Date('11/11/2011').toString(),
        end_time: new Date('11/11/2011').toString(),
        runs_summary: [ { count: 1 } as InstanceRunSummary ],
        alerts_summary: [],
      } as unknown as Instance, now)).toEqual({
        alerts_summary: [],
        end_time: new Date('11/11/2011'),
        errorAlertsCount: 0,
        runsCount: 1,
        runs_summary: [
          { 'count': 1 },
        ],
        start_time: new Date('11/11/2011'),
        warningAlertsCount: 0,
      });

    });

    it('should parse set end_date to now if it is not set', () => {

      const now = new Date();
      const startTime = new Date();
      startTime.setHours(0);
      startTime.setMinutes(0);
      startTime.setSeconds(0);

      expect(parseInstances({
        start_time: new Date('11/11/2011').toString(),
        runs_summary: [ { count: 1 } as InstanceRunSummary ],
        alerts_summary: [],
      } as unknown as Instance, now)).toEqual({
        alerts_summary: [],
        end_time: now,
        errorAlertsCount: 0,
        runsCount: 1,
        runs_summary: [
          { 'count': 1 },
        ],
        start_time: new Date('11/11/2011'),
        warningAlertsCount: 0,
      });
    });

    it('should parse an upcoming instance', () => {
      // receiving expected start and end time as ISO string
      // storing their `Date` version in start_time and end_time

      const now = new Date();

      const expected_start_time = new Date('11/11/2011 12:00');
      const expected_end_time = new Date('11/11/2011 15:00');

      expect(parseInstances({
        status: 'UPCOMING',
        expected_start_time: expected_start_time.toISOString(),
        expected_end_time: expected_end_time.toISOString(),
      } as unknown as Instance, now)).toEqual({
        id: expect.anything(),
        status: 'UPCOMING',
        expected_start_time: expected_start_time.toISOString(),
        expected_end_time: expected_end_time.toISOString(),
        end_time: expected_end_time,
        start_time: expected_start_time,
      });

    });

    it('should parse an upcoming instance without expected end time', () => {
      // when end time is not set we assume that fair length of 3 hours
      // so if expected start time is 12PM then we expect it to finish by 15PM

      const now = new Date();

      const expected_start_time = new Date('11/11/2011 12:00');

      expect(parseInstances({
        status: 'UPCOMING',
        expected_start_time: expected_start_time.toISOString(),
      } as unknown as Instance, now)).toEqual({
        id: expect.anything(),
        status: 'UPCOMING',
        expected_start_time: expected_start_time.toISOString(),
        end_time: new Date('11/11/2011 15:00'),
        start_time: expected_start_time,
      });

    });

    it('should parse an upcoming instance without expected start time', () => {
      // when expected start time is not set we assume that the instance is going to start soon

      const now = new Date();

      const expected_end_time = new Date('11/11/2011 12:00');
      const start_time = new Date('11/11/2011 11:00');

      expect(parseInstances({
        status: 'UPCOMING',
        expected_end_time: expected_end_time.toISOString(),
      } as unknown as Instance, now)).toEqual({
        id: expect.anything(),
        status: 'UPCOMING',
        expected_end_time: expected_end_time.toISOString(),
        end_time: expected_end_time,
        start_time,
      });

    });
  });
});
