import { Injectable } from '@angular/core';
import { BaseComponent, ComponentType, EntityActions, EntityState, EntityStore } from '@observability-ui/core';
import { Journey, JourneyInstanceRule } from '@observability-ui/core';
import { JourneysService } from '../../services/journeys/journeys.service';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { catchError, EMPTY, forkJoin, map, Observable, of, switchMap, throwError } from 'rxjs';

interface JourneyUpdateRequest {
  id: string;
  name: string;
  description: string;
  instance_rules: JourneyInstanceRule[];
}

interface JourneyCreateRequest {
  name: string,
  description: string,
  instance_rules: JourneyInstanceRule[],
  project_id: string
  components?: string[]
}

export interface JourneysActions extends EntityActions<Journey> {
  createOne: (req: JourneyCreateRequest) => Observable<Journey>;
  updateOne: (req: JourneyUpdateRequest) => Observable<Journey>;
  findComponents: (id: string, filters?: { component_type?: ComponentType[] }) => Observable<BaseComponent[]>;
}

interface JourneyState extends EntityState<Journey> {
  components: BaseComponent[];
}


@Injectable({
  providedIn: 'root'
})
export class JourneysStore extends EntityStore<JourneyState, JourneysActions> implements makeStore<JourneyState, JourneysActions> {

  components$ = this.select(({ components }) => components);

  constructor(protected service: JourneysService) {
    super({
      list: [],
      total: 0,
      components: [],
    });
  }

  @Effect()
  createOne({ name, description, instance_rules, project_id, components }: JourneyCreateRequest): Observable<Journey> {
    return this.service.create({ name, description }, project_id).pipe(
      switchMap((journey) => {
        if (instance_rules && instance_rules.length > 0) {
          return forkJoin(
            instance_rules.map((rule) => {
              return this.service.createInstanceRule(journey.id, rule);
            })
          ).pipe(
            catchError(() => {
              return throwError(() => new Error(`Error creating new instance condition. Try it again`));
            }),
            map((rules) => {
              return { ...journey, instance_rules: rules };
            }),
          );
        } else {
          return of(journey);
        }
      }),
      switchMap((journey) => {
        if (components && components.length > 0) {
          return forkJoin(
            components.map((component_id) => {
              return this.service.createJourneyDagEdge(journey.id, undefined, component_id);
            })
          ).pipe(
            catchError((err) => {
              console.log(err);
              return throwError(() => new Error(`Error adding component to dag. Try it again`));
            }),
            map(() => {
              return journey;
            }),
          );
        } else {
          return of(journey);
        }
      }),
    );

  }

  @Reduce()
  onCreateOne(state: JourneyState, payload: Journey) {
    return {
      ...state,
      list: [ ...state.list, payload ],
      total: state.total + 1,
    };
  }

  @Effect()
  updateOne({ instance_rules, ...journey }: JourneyUpdateRequest): Observable<Journey> {
    return this.service.getOne(journey.id).pipe(
      switchMap(({ instance_rules }) => {

        if (instance_rules && instance_rules.length > 0) {
          return forkJoin(
            instance_rules.map(({ id }) => this.service.deleteInstanceRule(id))
          );
        } else {
          return of(EMPTY);
        }
      }),
      switchMap(() => {
        if (instance_rules && instance_rules.length) {
          return forkJoin(
            instance_rules.map((rule) => {
              return this.service.createInstanceRule(journey.id, rule);
            })
          );
        } else {
          return of(EMPTY);
        }
      }),
      switchMap(() => {
        return this.service.update(journey);
      }),
    );
  }

  @Reduce()
  onUpdateOne(state: JourneyState, payload: Journey) {
    if (payload) {
      const idx = state.list.findIndex(({ id }) => id === payload.id);

      if (idx < 0) {
        console.error('this should never happen, just edited a journey which is not available anymore!');
      } else {
        state.list[idx] = payload;
      }
    }

    return {
      ...state,
      selected: payload,
    };
  }

  @Effect()
  findComponents(journeyId: string, filters?: { component_type?: ComponentType[] }): Observable<BaseComponent[]> {
    return this.service.getComponentsByJourney(journeyId, filters).pipe(
      map(({ entities }) => entities)
    );
  }

  @Reduce()
  onFindComponents(state: JourneyState, payload: BaseComponent[]): JourneyState {
    return {
      ...state,
      components: payload,
    };
  }

}
