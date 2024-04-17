import { Injectable } from '@angular/core';
import { EntityService, EntityType } from '@observability-ui/core';
import { Rule } from './rule.model';


@Injectable({
  providedIn: 'root'
})
export class RuleService extends EntityService<Rule> {
  protected override baseEntity: EntityType = EntityType.Rule;
  protected override parentEntity = EntityType.Journey;
}
