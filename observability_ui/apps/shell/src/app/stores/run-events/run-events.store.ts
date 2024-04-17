import { Injectable } from '@angular/core';
import { EntityActions, EntityState, EntityStore, EventType } from '@observability-ui/core';
import { RunEventsService } from '../../services/run-events/run-events.service';
import { makeStore } from '@microphi/store';

@Injectable({
  providedIn: 'root'
})
export class RunEventsStore extends EntityStore<EntityState<EventType>, EntityActions<EventType>> implements makeStore<EntityState<EventType>, EntityActions<EventType>> {
  constructor(protected service: RunEventsService) {
    super({
      list: [],
      total: 0,
    });
  }
}
