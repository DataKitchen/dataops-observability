import { Entity } from '../entity';
import { TestStatus } from './event.model';
import { Alert } from './alert.model';
import { BaseComponent } from './component.model';

export interface Run extends Entity {
  pipeline: Pick<BaseComponent, 'id' | 'name' | 'display_name'>;
  key: string;
  start_time: string;
  end_time: string;
  expected_start_time?: string;
  expected_end_time?: string;
  status: RunProcessedStatus;
  alerts?: RunAlert[];
  tasks_summary: RunTaskSummary[];
  tests_summary?: TestSummary[];
}

export interface RunTaskSummary {
  status: RunProcessedStatus,
  count: number;
}

export interface TestSummary {
  status: TestStatus;
  count: number;
}


export enum RunProcessedStatus {
  Pending = <any>'PENDING',
  Missing = <any>'MISSING',
  Running = <any>'RUNNING',
  Completed = <any>'COMPLETED',
  CompletedWithWarnings = <any>'COMPLETED_WITH_WARNINGS',
  Failed = <any>'FAILED',
}


export enum RunAlertType {
  LateStart = 'LATE_START',
  LateEnd = 'LATE_END',
  MissingRun = 'MISSING_RUN',
  CompletedWithWarnings = 'COMPLETED_WITH_WARNINGS',
  Failed = 'FAILED',
  UnexpectedStatusChange = 'UNEXPECTED_STATUS_CHANGE',
}

export type RunAlert = Alert<RunAlertType>;

export const runAlertTypesKeys = Object.keys(RunAlertType);

export interface RunTask extends Entity {
  start_time: string;
  end_time?: string;
  status: RunProcessedStatus;
  required: boolean;
  run: string;
  task: {
    id: string;
    key: string;
    display_name: string;
  }
}
