import { BaseComponent, ComponentType, EntityActions, EntityListResponse, EntityState, EntityStore, nonReadonlyFields, PaginatedRequest, Pagination, removeDuplicates, Schedule, SortOptions } from '@observability-ui/core';
import { Injectable } from '@angular/core';
import { concatMap, EMPTY, forkJoin, map, Observable, of, switchMap } from 'rxjs';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { ComponentsService } from '../../services/components/components.service';
import { pick } from '@datakitchen/ngx-toolkit';

export interface ComponentUI extends BaseComponent {
  // only PipeLines have expectations
  startsAt?: Schedule;
  endsAt?: Schedule;
  // only Dataset have expectedArrivalWindow
  expectedArrivalWindow?: Schedule;
}

interface ComponentActions extends EntityActions<ComponentUI> {
  create: (component: nonReadonlyFields<ComponentUI>, projectId: string) => Observable<ComponentUI>;

  deleteComponent: (id: string) => Observable<{ id: string }>;

  getOne: (id: string) => Observable<ComponentUI>;
  updateOne: (component: ComponentUI, extra: {
    expectedArrivalWindow?: Schedule,
    startsAt?: Schedule,
    endsAt?: Schedule,
  }, editExpectedSchedule?: boolean, editExpectedArrivalWindow?: boolean, editTool?: boolean) => Observable<ComponentUI>;

  searchPage: (req: PaginatedRequest, ids: string[]) => Observable<Array<ComponentUI>>;
}

interface ComponentState extends EntityState<ComponentUI> {
  // This property is needed to handle the filters. When calling `getOne` and then
  // `getPage`, the `getOne` result in `list` would be overwritten by the `getPage`
  // result. Instead calling `searchPage` will accumulate everything in `all`
  all: ComponentUI[];
}

@Injectable({
  providedIn: 'root',
})
export class ComponentStore extends EntityStore<ComponentState, ComponentActions> implements makeStore<ComponentState, ComponentActions> {
  allComponents$ = this.select(({ all }) => all);

  constructor(protected service: ComponentsService,) {
    super({
      list: [],
      total: 0,
      all: []
    });
  }

  @Effect()
  searchPage(req: PaginatedRequest, ids: string[]): Observable<Array<ComponentUI>> {
    return forkJoin([
      super.getPage(req).pipe(
        map(({ entities }) => {
          return entities;
        })
      ),
      ...ids.map((id) => this.getOne(id))
    ]).pipe(
      map(([ page, ...components ]) => {
        return [ ...page, ...components ];
      })
    );
  }

  @Reduce()
  onSearchPage(state: ComponentState, payload: Array<ComponentUI>) {
    return {
      ...state,
      all: removeDuplicates([ ...state.all, ...payload ], 'id')
    };
  }

  @Reduce()
  override onGetPage(state: ComponentState, payload: EntityListResponse<ComponentUI> & Pagination & SortOptions): ComponentState {
    return {
      ...state,
      list: payload.entities,
      total: payload.total,
      page: payload.page,
      count: payload.count,
      all: removeDuplicates([ ...state.all, ...payload.entities ], 'id')
    };
  }

  @Effect('concatMap')
  override getOne(id: string): Observable<ComponentUI> {

    return super.getOne(id).pipe(
      concatMap((component) => {

        // when the component is of below types it can have schedules associated with itself
        if (component.type === ComponentType.BatchPipeline || component.type === ComponentType.Dataset) {
          return this.service.getSchedules(id).pipe(
            map(({ entities }) => {


              if (component.type === ComponentType.BatchPipeline) {
                return {
                  ...component,
                  startsAt: entities?.find((schedule) => schedule?.expectation === 'BATCH_PIPELINE_START_TIME'),
                  endsAt: entities?.find((schedule) => schedule?.expectation === 'BATCH_PIPELINE_END_TIME'),
                };
              }

              if (component.type === ComponentType.Dataset) {
                return {
                  ...component,
                  expectedArrivalWindow: entities[0],
                };
              }

              return component;
            })
          );
        }

        return of(component);
      })
    );
  }

  @Effect()
  create(component: nonReadonlyFields<BaseComponent>, projectId: string): Observable<BaseComponent> {
    return this.service.create(component, projectId);
  }

  @Reduce()
  onCreate(state: ComponentState, payload: BaseComponent): ComponentState {
    return {
      ...state,
      all: [ ...state.all, payload ],
      list: [ ...state.list, payload ],
      total: state.total + 1,
    };
  }

  @Effect('mergeMap')
  updateOne(
    component: BaseComponent,
    schedules?: {
      startsAt?: Schedule;
      endsAt?: Schedule;
      expectedArrivalWindow?: Schedule;
    },
    editExpectedSchedule: boolean = true,
    editExpectedArrivalWindow: boolean = true,
  ): Observable<ComponentUI> {
    return this.service.getSchedules(component.id).pipe(
      switchMap(({ entities: schedules }) => {
        if (editExpectedArrivalWindow || editExpectedSchedule) {
          const calls = schedules.map((existingSchedule) => this.service.deleteSchedule(existingSchedule.id));

          if (calls.length > 0) {
            return forkJoin(calls);
          }
        }

        return of(EMPTY);
      }),
      switchMap(() => {
        if (editExpectedSchedule || editExpectedArrivalWindow) {
          const calls: Observable<any>[] = [];

          if (schedules?.startsAt) {
            calls.push(this.service.createSchedule(component.id, {
              ...pick(schedules.startsAt, [ 'timezone', 'schedule', 'margin' ]),
              expectation: 'BATCH_PIPELINE_START_TIME'
            }));
          }

          if (schedules?.endsAt) {
            calls.push(this.service.createSchedule(component.id, {
              ...pick(schedules.endsAt, [ 'timezone', 'schedule', 'margin' ]),
              expectation: 'BATCH_PIPELINE_END_TIME'
            }));
          }

          if (schedules?.expectedArrivalWindow) {
            calls.push(this.service.createSchedule(component.id, {
              ...pick(schedules.expectedArrivalWindow, [ 'timezone', 'schedule', 'margin' ]),
              expectation: 'DATASET_ARRIVAL'
            }));
          }

          if (calls.length > 0) {
            return forkJoin(calls);
          }
        }

        return of([]);
      }),
      switchMap((schedules: Schedule[]) => {
        return this.service.update(component).pipe(
          map((comp) => {
            let componentSchedules = {};

            if (editExpectedSchedule || editExpectedArrivalWindow) {
              componentSchedules = {
                startsAt: schedules.find((schedule) => schedule?.expectation === 'BATCH_PIPELINE_START_TIME'),
                endsAt: schedules.find((schedule) => schedule?.expectation === 'BATCH_PIPELINE_END_TIME'),
                expectedArrivalWindow: schedules.find((schedule) => schedule?.expectation === 'DATASET_ARRIVAL'),
              };
            }

            return {
              ...comp,
              ...componentSchedules
            };
          })
        );
      }),
    );
  }

  @Reduce()
  onUpdateOne(state: ComponentState, component: ComponentUI): ComponentState {
    // update component info
    const entityIdx = state.list.findIndex((e) => e.id === component.id);
    const allEntityIdx = state.all.findIndex((e) => e.id === component.id);

    if (entityIdx >= 0) {
      state.list[entityIdx] = component;
    }

    if (allEntityIdx >= 0) {
      state.all[entityIdx] = component;
    }

    return { ...state, selected: component };
  }

  @Effect('mergeMap')
  deleteComponent(id: string): Observable<{ id: string }> {
    return this.service.delete(id);
  }

  @Reduce()
  onDeleteComponent(state: ComponentState, payload: { id: string }): ComponentState {
    const entityIdx = state.list.findIndex((e) => e.id === payload.id);

    const list = state.list;
    list.splice(entityIdx, 1);

    return { ...state, list, total: state.total - 1, selected: undefined };
  }
}
