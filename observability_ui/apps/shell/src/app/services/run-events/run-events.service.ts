import { Injectable } from '@angular/core';
import { EntityService, EntityType, EventType } from '@observability-ui/core';

@Injectable({
  providedIn: 'root'
})
export class RunEventsService extends EntityService<EventType> {

  protected override parentEntity = EntityType.Run;
  protected override baseEntity = EntityType.Event;
}
