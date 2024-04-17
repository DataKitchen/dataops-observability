import { AlertLevel, TestOutcomeItem } from '../models';
import { Instance, isInstance, TodayInstance, UpcomingInstance } from '../models/instance.model';

export interface RemappedInstanceAlert<T> {
  count: number;
  alerts: T[];
}

interface Summary {
  status: string;
  count: number;
}

interface TestsByComponent {
  [componentId: string]: TestOutcomeItem[];
}

export function aggregateAlerts<T extends { level: AlertLevel; count: number }>(alerts: Array<T>): {
  errors: RemappedInstanceAlert<T>;
  warnings: RemappedInstanceAlert<T>
} {
  const errorAlerts = alerts.filter(x => x.level === 'ERROR');
  const warningAlerts = alerts.filter(x => x.level === 'WARNING');

  return {
    errors: {
      count: errorAlerts.reduce((a, b) => a + b.count, 0),
      alerts: errorAlerts,
    },
    warnings: {
      count: warningAlerts.reduce((a, b) => a + b.count, 0),
      alerts: warningAlerts,
    },
  };
}

export function getSummary(entities: Array<{ status: string }>): Summary[] {
  return Array.from(entities.reduce((map, entity) => map.set(entity.status, (map.get(entity.status) ?? 0) + 1), new Map<string, number>()).entries()).map(([ status, count ]) => ({
    status,
    count
  }));
}

export function testsByComponent(tests: TestOutcomeItem[]): TestsByComponent {
  const groups = {} as TestsByComponent;
  const result = tests.reduce((g, test) => {
    if (test.component) {
      if (!g[test.component.id]) {
        g[test.component.id] = [];
      }

      g[test.component.id].push(test);
    }

    return g;
  }, groups);

  return result;
}

export function parseInstances(instance: Instance | UpcomingInstance, now: Date): TodayInstance {

  if (isInstance(instance)) {

    const alertsSummary = aggregateAlerts(instance.alerts_summary);

    return {
      ...instance,
      start_time: new Date(instance.start_time),
      end_time: instance.end_time ? new Date(instance.end_time)
        : instance.expected_end_time ? new Date(instance.expected_end_time) : now,

      runsCount: instance.runs_summary?.reduce((total, summary) => total + summary.count, 0) ?? 0,
      errorAlertsCount: alertsSummary.errors.count,
      warningAlertsCount: alertsSummary.warnings.count,
    };

  } else {
    const upInst = instance as UpcomingInstance;

    let start_time;

    if (upInst.expected_start_time) {
      start_time = new Date(upInst.expected_start_time);
    } else {

      // assuming that an upcoming instance must have expected_end_time
      // if expected_start_time is not set
      start_time = new Date(upInst.expected_end_time);
      start_time.setHours(start_time.getHours() - 1);
    }

    let end_time;
    if (upInst.expected_end_time) {
      end_time = new Date(upInst.expected_end_time);
    } else {
      const endTime = new Date(start_time);
      endTime.setHours(start_time.getHours() + 3);
      end_time = endTime;
    }

    return {
      ...instance,
      id: Math.random().toString(36).slice(2),
      start_time,
      end_time,
      status: 'UPCOMING',
    };
  }
}
