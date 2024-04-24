import { Entity } from '../../entity';

export interface Agent extends Entity {
  key: string;
  tool: string;
  version: string;
  latest_heartbeat: string;
  latest_event_timestamp?: string;
}
