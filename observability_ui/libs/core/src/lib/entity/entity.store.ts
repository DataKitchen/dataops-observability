import { Entity, EntityListResponse, FindAllRequest, PaginatedRequest, Pagination, SortOptions, WithId } from './entity.model';
import { distinctUntilChanged, filter, map, Observable, of } from 'rxjs';
import { Effect, Reduce, Store } from '@microphi/store';
import { EntityService } from './entity.service';

export interface EntityState<T> extends Pagination, SortOptions {
  list: T[];
  total: number;
  selected?: T;
}

export interface EntityActions<E> {
  getPage: (req: PaginatedRequest) => Observable<EntityListResponse<E> & Pagination & SortOptions>;
  findAll: (req: FindAllRequest) => Observable<EntityListResponse<E>> & Pagination & SortOptions;
  getOne: (id: string) => Observable<E>;
  reset: () => Observable<undefined>;
  deleteOne: (id: string) => Observable<WithId>;
}

export const entityStoreInitialState: {
  list: any[];
  total: number;
} = {
  list: [],
  total: 0,
};

export abstract class EntityStore<State extends EntityState<E>,
  A extends EntityActions<any>,
  E extends Entity = State extends EntityState<infer Ent> ? Ent : Entity,
> extends Store<State, A> {

  list$: Observable<E[]> = this.select(({ list }) => list);
  total$: Observable<number> = this.select(({ total }) => total);

  selected$: Observable<E> = this.select(({ selected }) => selected).pipe(
    filter(Boolean),
    distinctUntilChanged((previous, current) => {
      return JSON.stringify(previous) === JSON.stringify(current);
    })
  );

  // TODO set default pagination primitives somewhere
  page$ = this.select(({ page }) => page || 0); // page -> 0-indexed
  count$ = this.select(({ count }) => count || 10);
  order$ = this.select(({ sort }) => sort);
  // sortBy$ = this.select(({sort_by}) => sort_by);

  protected abstract service: EntityService<E>;

  getEntity(id: string): Observable<E | undefined> {
    return this.state$.pipe(
      map(({ list }) => {
        return list.find((e) => e.id === id);
      })
    );
  }

  @Effect('concatMap')
  getOne(id: string): Observable<E> {
    return this.service.getOne(id);
  }

  @Reduce()
  onGetOne(state: State, payload: E): State {

    if (payload) {

      const entityIdx = state.list.findIndex((e) => e['id'] === payload.id);
      if (entityIdx >= 0) {
        state.list[entityIdx] = payload;
      } else {
        state.list.push(payload);
        state.total++;
      }
    }

    return {
      ...state,
      selected: payload,
    };
  }

  @Effect()
  findAll(req?: FindAllRequest) {
    return this.service.findAll(req);
  }

  @Reduce()
  onFindAll(state: State, payload: EntityListResponse<E>): State {
    return {
      ...state,
      list: payload.entities,
      total: payload.total,
    };
  }

  @Effect()
  getPage(req: PaginatedRequest) {
    return this.service.getPage(req).pipe(
      map((resp) => {
        return {
          ...resp,

          // merge with pagination info so that we set them in the state
          page: req.page,
          count: req.count,
          sort: req.sort,
          // sort_by: req.sort_by,
        };
      }),
    );
  }

  @Reduce()
  onGetPage(state: State, payload: EntityListResponse<E> & Pagination & SortOptions): State {
    return {
      ...state,
      list: payload.entities,
      total: payload.total,
      page: payload.page,
      count: payload.count,
      // sort_by: payload.sort_by,
    };
  }

  @Effect()
  reset() {
    return of(undefined);
  }

  @Reduce()
  onReset(): State {
    return this['initialState'];
  }

  @Effect()
  deleteOne(id: string): Observable<WithId> {
    return this.service.delete(id);
  }

  @Reduce()
  onDeleteOne(state: State, payload: WithId): State {
    const idx = state.list.findIndex(({ id }) => id === payload.id);

    state.list = state.list.filter((value, index) => {
      return index !== idx;
    });

    state.total--;

    return state;
  }

}
