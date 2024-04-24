import { EntityActions, EntityListResponse, EntityState, EntityStore, PaginatedRequest } from '../../entity';
import { Project } from './project.model';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { ProjectService } from './project.service';
import { map, Observable, scan } from 'rxjs';
import { Injectable } from '@angular/core';
import { EventSearchFields, EventType, TestOutcomeItem } from '../../models/event.model';

export interface State extends EntityState<Project> {
  events: {
    list: EventType[];
    total: number;
  };
  selectedTest: TestOutcomeItem | null;
}

interface Actions extends EntityActions<Project> {
  getEventsByPage: (req: PaginatedRequest<EventSearchFields>) => Observable<EntityListResponse<EventType>>;
  createOne: (project: Pick<Project, 'name' | 'description'>, organizationId: string) => Observable<Project>;
  updateOne: ({ id, name, description }: { id: string; name: string; description: string }) => Observable<Project>;
  selectTest: (testId: string) => Observable<TestOutcomeItem>;
}

@Injectable({
  providedIn: 'root',
})
export class ProjectStore extends EntityStore<State, Actions> implements makeStore<State, Actions> {
  events$ = this.select(({ events }) => events.list);
  totalEvents$ = this.select(({ events }) => events.total);
  selectedTest$ = this.select(({ selectedTest }) => selectedTest);

  current$ = this.selected$;

  projectChanged$ = this.select(({ selected }) => selected).pipe(

    scan((lastTwoProjects, currentProject) => this.reduceBuffer(lastTwoProjects, currentProject), [ undefined, undefined ] as (Project | undefined)[]),
    map(([ previous, current ]) => this.projectChanged(previous, current)),
  );

  constructor(protected service: ProjectService) {
    super({
      list: [],
      total: 0,
      selected: JSON.parse(localStorage.getItem('selectedProject') || 'null'),
      events: {
        list: [],
        total: 0,
      },
      selectedTest: null
    });
  }

  @Reduce()
  override onGetOne(state: State, payload: Project): State {

    if (state.selected?.id !== payload.id) {
      // changing current project
      state.events.list = [];
      state.events.total = 0;
    }

    localStorage.setItem('selectedProject', JSON.stringify(payload));

    return super.onGetOne(state, payload);
  }

  @Reduce()
  override onReset(): State {
    localStorage.removeItem('selectedProject');
    return {
      list: [],
      total: 0,
      events: {
        list: [],
        total: 0,
      },
      selectedTest: null
    };
  }

  @Effect()
  getEventsByPage(req: PaginatedRequest<EventSearchFields>) {
    return this.service.getEvents(req);
  }

  @Reduce()
  onGetEventsByPage(state: State, payload: EntityListResponse<EventType>): State {
    return {
      ...state,
      events: {
        list: payload.entities,
        total: payload.total,
      },
    };
  }

  @Effect()
  createOne(project: Pick<Project, 'name' | 'description'>, organizationId: string): Observable<Project> {
    return this.service.create(project, organizationId);
  }

  @Reduce()
  onCreateOne(state: State, payload: Project): State {

    const list = state.list.concat(payload);
    const total = state.total + 1;

    return {
      ...state,
      list,
      total,
    };
  }

  @Reduce()
  override onFindAll(state: State, payload: EntityListResponse<Project>): State {
    const selected = state.selected ||
      payload.entities.find(({ name }) => name === 'default') ||
      payload.entities[0];
    return super.onFindAll({ ...state, selected }, payload);
  }

  @Effect()
  updateOne({ ...project }: { id: string; name: string; description: string; }): Observable<Project> {
    return this.service.update(project);
  }

  @Reduce()
  onUpdateOne(state: State, payload: Project) {
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
  selectTest(testId: string): Observable<TestOutcomeItem> {
    return this.service.getTestById(testId);
  }

  @Reduce()
  onSelectTest(state: State, selectedTest: TestOutcomeItem): State {
    return { ...state, selectedTest };
  }

  private reduceBuffer(lastTwoProjects: (Project | undefined)[], currentProject: Project | undefined) {

    lastTwoProjects.push(currentProject);
    // only keep the last two elements
    lastTwoProjects = lastTwoProjects.slice(-2);

    return lastTwoProjects;
  }

  // only when it changes the first time `previous` can be undefined
  private projectChanged(previous: Project|undefined, current: Project|undefined) {
    if (previous === undefined) {
      return false; // first change does not count as a change
    }

    return previous.id !== current?.id;
  }}
