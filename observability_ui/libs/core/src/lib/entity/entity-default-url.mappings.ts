import { EntityType } from './entity-type';

export const entityDefaultUrlMappings: Record<string, string> = {
  [EntityType.User]: 'users',
  [EntityType.Company]: 'companies',
  [EntityType.Organization]: 'organizations',
  [EntityType.Project]: 'projects',
  [EntityType.Event]: 'events',
  [EntityType.Pipeline]: 'pipelines',
  [EntityType.Run]: 'runs',
  [EntityType.Task]: 'tasks',
  [EntityType.Rule]: 'rules',
  [EntityType.Journey]: 'journeys',
  [EntityType.Instance]: 'instances',
  [EntityType.Component]: 'components',
  [EntityType.ServiceKey]: 'service-account-key',
  [EntityType.Dashboards]: 'dashboards',
  [EntityType.Agent]: 'agents',
};
