import { Injectable } from '@angular/core';
import { EntityService, EntityType } from '../../../entity';
import { Agent } from '../agent.model';


@Injectable({
  providedIn: 'root'
})
export class AgentService extends EntityService<Agent>{
  protected readonly baseEntity = EntityType.Agent;
  protected override readonly parentEntity = EntityType.Project;
}
