import { Injectable } from '@angular/core';
import { EntityActions, EntityState, EntityStore, ServiceKey, WithId } from '@observability-ui/core';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { APIKeysService } from './api-keys.service';
import { Observable, of } from 'rxjs';

interface APIKeysState extends EntityState<ServiceKey> {
  token?: string;
}

interface APIKeysActions extends EntityActions<ServiceKey> {
  create: (key: {
    name: string,
    expires_after_days: string;
    allowed_services: Array<'EVENTS_API' | 'OBSERVABILITY_API'>
  }, projectId: string) => Observable<ServiceKey>;
  clearToken: () => Observable<undefined>;
}

@Injectable({
  providedIn: 'root'
})
export class APIKeysStore extends EntityStore<APIKeysState, APIKeysActions> implements makeStore<APIKeysState, APIKeysActions> {
  token$ = this.select(state => state.token);

  constructor(protected service: APIKeysService) {
    super({
      list: [],
      total: 0,
    });
  }

  @Effect()
  create(key: {
    name: string,
    expires_after_days: string;
    allowed_services: Array<'EVENTS_API' | 'OBSERVABILITY_API'>
  }, projectId: string): Observable<ServiceKey> {
    return this.service.create(key, projectId);
  }

  @Reduce()
  onCreate(state: EntityState<ServiceKey>, payload: ServiceKey): APIKeysState {
    return {
      ...state,
      list: [ ...state.list, payload ],
      total: state.total + 1,
      token: payload.token
    };
  }

  @Effect()
  clearToken(): Observable<undefined> {
    return of(undefined);
  }

  @Reduce()
  onClearToken(state: APIKeysState): APIKeysState {
    return { ...state, token: null };
  }

  @Effect('mergeMap')
  override deleteOne(id: string): Observable<WithId> {
    return super.deleteOne(id);
  }
}
