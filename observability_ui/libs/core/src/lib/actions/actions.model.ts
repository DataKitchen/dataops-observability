import { InjectionToken } from '@angular/core';
import { RunProcessedStatus } from '../models';
import { AbstractAction } from './abstract-action/abstract-action.directive';

export const TaskStatusEmailTemplate = {
  [RunProcessedStatus.Running]: 'task_status_started',
  [RunProcessedStatus.Completed]: 'task_status_completed',
  [RunProcessedStatus.CompletedWithWarnings]: 'task_status_warning',
  [RunProcessedStatus.Failed]: 'task_status_error',
};

export const RULE_ACTIONS = new InjectionToken<typeof AbstractAction[]>('RULE_ACTIONS');
