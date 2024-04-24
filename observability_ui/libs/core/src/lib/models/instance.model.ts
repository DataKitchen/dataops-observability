import { Entity } from '../entity/entity.model';
import { Project } from '../services/project/project.model';
import { Alert, AlertLevel } from './alert.model';
import { ComponentType } from './component.model';
import { EventType, TestStatus } from './event.model';
import { RunProcessedStatus, TestSummary } from './runs.model';
import { JourneyDagNode } from './journey.model';

export interface Instance extends Entity {
  start_time: string;
  end_time: string;
  expected_end_time?: string;
  journey: {
    name: string,
    id: string
  };

  runs_summary?: Array<InstanceRunSummary>;
  tests_summary?: Array<InstanceTestSummary>;
  alerts_summary: Array<AlertSummary>;
  project: Project;
  status: InstanceStatus;
  payload_key?: string;
  start_type?: string;
}

export enum InstanceStatus {
  Error = 'ERROR',
  Warning = 'WARNING',
  Active = 'ACTIVE',
  Completed = 'COMPLETED',
  Upcoming = 'UPCOMING',
}


export interface InstanceRunSummary {
  status: RunProcessedStatus;
  count: number;
}


export interface InstanceTestSummary {
  status: TestStatus;
  count: number;
}

export interface InstanceAlertComponent {
  id: string;
  display_name: string;
  type: ComponentType;
}

export type InstanceAlert = Alert<InstanceAlertType> & {
  components?: InstanceAlertComponent[];
};


export enum InstanceAlertType {
  LateStart = 'LATE_START',
  LateEnd = 'LATE_END',
  Incomplete = 'INCOMPLETE',
  OutOfSequence = 'OUT_OF_SEQUENCE',
  DatasetNotReady = 'DATASET_NOT_READY',
  TestsFailed = 'TESTS_FAILED',
  TestsHadWarnings = 'TESTS_HAD_WARNINGS',
}

export interface InstanceDagNode extends JourneyDagNode {
  status: RunProcessedStatus;
  runs_count: number;
  runs_summary: InstanceRunSummary[];
  tests_summary: TestSummary[];
  tests_count: number;
  events?: EventType[];
}

export interface AlertSummary {
  count: number;
  description: string;
  level: AlertLevel;
}

export interface UpcomingInstance {
  project?: {
    id: string;
    name: string;
  };
  expected_start_time: string;
  expected_end_time: string;
  journey: {
    id: string;
    name: string;
  };
  status: 'UPCOMING';
}

export function isInstance(i: object): i is Instance {
  return !!(i as Instance).start_time;
}

export function isUpcomingInstance(i: object): i is UpcomingInstance {
  return !!((i as UpcomingInstance).expected_start_time || (i as UpcomingInstance).expected_end_time);
}

export interface TodayInstance {
  id: string;
  start_time: Date;
  end_time: Date;
  expected_start_time?: string;
  expected_end_time?: string;
  errorAlertsCount?: number;
  warningAlertsCount?: number;
  runsCount?: number;
  active?: boolean;
  project?: {
    id: string;
    name: string;
  };
  journey: {
    id: string;
    name: string;
  };
  status: InstanceStatus | 'UPCOMING';
}

export interface InstancesSearchFields {
  project_id?: string[];
  journey_id?: string[];
  active?: boolean;
  start_range_begin?: string;
  start_range_end?: string;
  end_range_begin?: string;
  end_range_end?: string;
  journey_name?: string[];
  status?: InstanceStatus[];
}

export interface UpcomingInstancesSearchFields {
  start_range: string;
  end_range?: string;
  journey_id?: string[];
  project_id?: string[];
  journey_name?: string[];
}
