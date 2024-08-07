import { AbstractAction, WithId } from '@observability-ui/core';
import { AbstractRule } from './abstract.rule';
import { InjectionToken } from '@angular/core';

export interface Rule extends WithId {
  component?: string;
  task?: string;
  action: string;
  action_args: any;
  rule_data: {
    when: 'all';
    conditions: Array<{
      [taskName: string]: any;
    }>;
  };
  rule_schema: string;

  parentId: string;
}

export type RuleType = 'task_status' | 'run_state' | 'metric_log' | 'message_log' | 'test_status' | 'instance_alert';

export type RuleUI = {
  id: string;
  actions: { component: typeof AbstractAction, data: any; editing?: boolean, expanded?: boolean }[];
  conditions: { key: any; value: any; }[];
}

export const RULES = new InjectionToken<typeof AbstractRule[]>('RULES');
