import { Entity } from '../../entity';

export interface Agent extends Entity {
  key: string;
  tool: string;
  version: string;
  status: AgentStatus;
  latest_heartbeat: string;
  latest_event_timestamp?: string;
}

export enum AgentStatus {
  Online = 'ONLINE',
  Unhealthy = 'UNHEALTHY',
  Offline = 'OFFLINE',
}
