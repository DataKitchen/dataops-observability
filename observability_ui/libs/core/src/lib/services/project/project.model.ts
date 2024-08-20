import { Entity, WithId } from '../../entity';

export interface Project extends Entity {
  organization: string;
}

export interface ServiceKey extends WithId {
  project: string;
  name: string;
  service_name?: string;
  description?: string;
  expires_at: string;
  token?: string;
  allowed_services?: Array<'EVENTS_API' | 'OBSERVABILITY_API' | 'AGENT_API'>
}

export interface ProjectAlertSettingsAction {
  action_impl: string,
  action_args: any,
}

export interface ProjectAlertSettings {
  agent_check_interval: number;
  actions: ProjectAlertSettingsAction[];
}

export interface TestsSearchFields {
  start_range_begin?: string;
  start_range_end?: string;
  end_range_begin?: string;
  end_range_end?: string;
  status?: string;
  search?: string;
  instance_id?: string;
  component_id?: string;
  run_id?: string;
  key?: string;
}

export interface AlertsSearchFields {
  type?: string;
  level?: string;
  date_range_start?: string;
  date_range_end?: string;
  instance_id?: string;
  component_id?: string;
  run_id?: string;
  run_key?: string;
}
