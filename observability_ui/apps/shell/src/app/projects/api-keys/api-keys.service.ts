import { Injectable } from '@angular/core';
import { EntityService, EntityType, ServiceKey } from '@observability-ui/core';

@Injectable({
  providedIn: 'root'
})
export class APIKeysService extends EntityService<ServiceKey> {

  protected override parentEntity = EntityType.Project;
  protected override baseEntity = EntityType.ServiceKey;
}
