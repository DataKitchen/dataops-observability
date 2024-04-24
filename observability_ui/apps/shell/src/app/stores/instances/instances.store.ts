import { Injectable } from '@angular/core';
import { AlertsSearchFields, BaseComponent, EntityActions, EntityListResponse, EntityState, EntityStore, FindAllRequest, Instance, InstanceAlert, InstanceAlertType, InstanceDagNode, InstancesSearchFields, InstanceStatus, isToday, isFutureDay, JourneyDagEdge, JourneyDagNode, PaginatedRequest, Pagination, ProjectService, Run, RunProcessedStatus, SortOptions, TestOutcomeItem, TestsSearchFields, UpcomingInstance } from '@observability-ui/core';
import { InstancesService } from '../../services/instances/instances.service';
import { catchError, defer, forkJoin, iif, map, Observable, of } from 'rxjs';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { ProjectRunsService } from '../../services/project-runs/project-runs.service';
import { ComponentsService } from '../../services/components/components.service';

export interface InstanceActions extends EntityActions<Instance> {
  findAllWithUpcoming: (req: FindAllRequest<InstancesSearchFields>) => Observable<(Instance | UpcomingInstance)[]>;
  findAllBachRuns: (projectId: string, instanceId: string) => Observable<EntityListResponse<Run> & Pagination & SortOptions>;
  clearBatchRuns: () => Observable<undefined>;
  getTestsByPage: (projectId: string, req: PaginatedRequest<TestsSearchFields>) => Observable<EntityListResponse<TestOutcomeItem> & Pagination & SortOptions>;
  getOutOfSequenceAlert: (projectId: string, instanceId: string) => Observable<InstanceAlert | undefined>;
  findComponents: (journeyId: string) => Observable<BaseComponent[]>;
  getDayInstances: (req: FindAllRequest, date?: Date, journey_id?: string[]) => Observable<(Instance | UpcomingInstance)[]>;
  getDayInstanceRuns: (projectId: string, instances: string[], date?: Date) => Observable<Run[]>;
  getAlertsByPage: (projectId: string, instanceId: string, req: PaginatedRequest<AlertsSearchFields>) => Observable<EntityListResponse<InstanceAlert> & Pagination & SortOptions>;
}

type CombinedResponse = Observable<EntityListResponse<Instance | UpcomingInstance>>[];


interface InstanceState extends EntityState<Instance> {
  runs: EntityState<Run>;
  dag: {
    nodes: {
      [k: string]: {
        info: JourneyDagNode; details?: InstanceDagNode
      };
    };
    edges: JourneyDagEdge[];
  };
  tests: EntityState<TestOutcomeItem>;
  alerts: { outOfSequence?: InstanceAlert };
  components: BaseComponent[];
  todayInstances: (Instance | UpcomingInstance)[];
  organizationInstances: Instance[];
  instanceAlerts: EntityState<InstanceAlert>;
}

@Injectable({
  providedIn: 'root'
})
export class InstancesStore extends EntityStore<InstanceState, InstanceActions> implements makeStore<InstanceState, InstanceActions> {
  runs$ = this.select(({ runs }) => runs.list);
  runsPage$ = this.select(({ runs }) => runs.page);
  runsCount$ = this.select(({ runs }) => runs.count);
  runsTotal$ = this.select(({ runs }) => runs.total);

  dagNodes$ = this.select(({ dag }) => Object.values(dag.nodes));
  dagEdges$ = this.select(({ dag }) => dag.edges);

  tests$ = this.select(({ tests }) => tests.list);
  testsTotal$ = this.select(({ tests }) => tests.total);

  outOfSequenceAlert$ = this.select(({ alerts }) => alerts.outOfSequence);

  components$ = this.select(({ components }) => components);

  todayInstances$ = this.select(({ todayInstances }) => todayInstances);

  instanceAlerts$ = this.select(({ instanceAlerts }) => instanceAlerts.list);
  instanceAlertsTotal$ = this.select(({ instanceAlerts }) => instanceAlerts.total);

  constructor(
    protected service: InstancesService,
    private runsService: ProjectRunsService,
    private projectService: ProjectService,
    private componentService: ComponentsService
  ) {
    super({
      list: [],
      total: 0,
      runs: {
        list: [],
        total: 0,
      },
      dag: {
        nodes: {},
        edges: [],
      },
      tests: {
        list: [],
        total: 0,
      },
      alerts: {
        outOfSequence: undefined,
      },
      instanceAlerts: {
        list: [],
        total: 0
      },
      components: [],
      todayInstances: [],
      organizationInstances: []
    });
  }

  @Effect()
  findAllBachRuns(projectId: string, instanceId: string): Observable<EntityListResponse<Run>> {
    return this.runsService.findAll({ parentId: projectId, filters: { instance_id: instanceId } });
  }

  @Reduce()
  onFindAllBachRuns(state: InstanceState, { entities, total }: EntityListResponse<Run>): InstanceState {
    return { ...state, runs: { list: entities, total } };
  }

  @Effect()
  clearBatchRuns(): Observable<undefined> {
    return of(undefined);
  }

  @Reduce()
  onClearBatchRuns(state: InstanceState): InstanceState {
    return { ...state, runs: { list: [], total: 0 } };
  }

  @Effect()
  findComponents(journeyId: string): Observable<BaseComponent[]> {
    return this.service.getComponents(journeyId).pipe(
      map(({ entities }) => entities),
    );
  }

  @Reduce()
  onFindComponents(state: InstanceState, components: BaseComponent[]): InstanceState {
    return { ...state, components };
  }

  @Effect()
  getTestsByPage(projectId: string, req: PaginatedRequest<TestsSearchFields>) {
    return this.projectService.getTests({ ...req, parentId: projectId }).pipe(
      map((response) => {
        return {
          ...response,
          page: req.page,
          count: req.count,
          sort: req.sort,
        };
      }),
    );
  }

  @Reduce()
  onGetTestsByPage(state: InstanceState, {
    entities,
    total,
    page,
    count,
    sort
  }: EntityListResponse<TestOutcomeItem> & Pagination & SortOptions): InstanceState {
    return { ...state, tests: { ...state.tests, list: entities, total, page, count, sort } };
  }

  @Effect()
  getAlertsByPage(projectId: string, instanceId: string, req: PaginatedRequest<AlertsSearchFields>) {
    return this.projectService.getAlerts({
      ...req,
      parentId: projectId,
      filters: { ...req.filters, instance_id: instanceId }
    }).pipe(
      map((response) => {
        return {
          ...response,
          page: req.page,
          count: req.count,
          sort: req.sort,
        };
      }),
    );
  }

  @Reduce()
  onGetAlertsByPage(state: InstanceState, {
    entities,
    total,
    page,
    count,
    sort
  }: EntityListResponse<InstanceAlert> & Pagination & SortOptions): InstanceState {
    return { ...state, instanceAlerts: { ...state.instanceAlerts, list: entities, total, page, count, sort } };
  }

  @Effect()
  getOutOfSequenceAlert(projectId: string, instanceId: string) {
    return this.projectService.getAlerts({
      parentId: projectId,
      filters: { instance_id: instanceId, type: InstanceAlertType.OutOfSequence },
      count: 1
    }).pipe(
      map((response) => {
        const alert = response.entities[0];
        return alert;
      }),
    );
  }


  @Reduce()
  onGetOutOfSequenceAlert(state: InstanceState, outOfSequence: InstanceAlert): InstanceState {
    return { ...state, alerts: { outOfSequence } };
  }

  @Effect()
  getDayInstances(req: FindAllRequest, date?: Date, journey_id?: string[]): Observable<(Instance | UpcomingInstance)[]> {
    const reference = date ?? new Date();
    const start = new Date(reference.setHours(0, 0, 0, 0));
    const end = new Date(reference.setHours(23, 59, 59, 999));

    // please bear in mind that when reference.setHours is called its value changes
    const upInstanceStart = isToday(reference) ? new Date() : start;

    return forkJoin([
      this.service.findAll({
        ...req,
        filters: {
          end_range_begin: start.toISOString(),
          end_range_end: end.toISOString(),
          journey_id,
        }
      }),
      this.service.findAll({
        ...req,
        filters: {
          active: true,
          start_range_end: end.toISOString(),
          journey_id,
        }
      }),
      iif(
        () => isToday(upInstanceStart) || isFutureDay(upInstanceStart),
        defer(() =>
          this.service.findUpcomingInstances({
            project_id: [ req.parentId ],
            journey_id: journey_id,
            start_range: upInstanceStart.toISOString(),
            end_range: end.toISOString(),
          }).pipe(
            catchError((err) => {
              console.log(err);
              return of({ entities: [] });
            })
          )
        ),
        of({ entities: [] }),
      ),
    ]).pipe(
      map(([
             todayInstances,
             activeInstances,
             upcoming ]) => {
        return [ ...todayInstances.entities, ...activeInstances.entities, ...upcoming.entities ];
      }),
    );
  }

  @Reduce()
  onGetDayInstances(state: InstanceState, todayInstances: (Instance | UpcomingInstance)[]): InstanceState {
    return {
      ...state,
      todayInstances,
    };
  }

  @Effect()
  getDayInstanceRuns(projectId: string, instances: string[], date?: Date): Observable<Run[]> {
    const reference = date ?? new Date();
    const start = new Date(reference.setHours(0, 0, 0, 0));
    const end = new Date(reference.setHours(23, 59, 59, 999));
    const defaultResponse: EntityListResponse<any> = { entities: [], total: 0 };

    return forkJoin([
      this.runsService.findAll({
        parentId: projectId,
        filters: { instance_id: instances, end_range_begin: start.toISOString(), end_range_end: end.toISOString() }
      }).pipe(
        catchError(() => of(defaultResponse)),
      ),
      this.runsService.findAll({
        parentId: projectId,
        filters: { instance_id: instances, status: [ RunProcessedStatus.Running ] }
      }).pipe(
        catchError(() => of(defaultResponse)),
      ),
    ]).pipe(
      map(([ todayRuns, listenigRuns ]) => [ ...todayRuns.entities, ...listenigRuns.entities ]),
    );
  }

  @Reduce()
  onGetDayInstanceRuns(state: InstanceState, todayInstanceRuns: Run[]): InstanceState {
    return {
      ...state,
      runs: {
        page: 0,
        list: todayInstanceRuns,
        total: todayInstanceRuns.length,
        count: todayInstanceRuns.length,
      },
    };
  }

  @Effect()
  findAllWithUpcoming({ filters }: FindAllRequest<InstancesSearchFields>): Observable<(Instance | UpcomingInstance)[]> {
    const now = new Date();
    const start = filters.start_range_begin ? new Date(filters.start_range_begin) : new Date();
    const end = filters.start_range_end ? new Date(filters.start_range_end) : undefined;

    const upInstanceStart = isToday(start) ? now : start;

    const findInstances = this.service.findAll({ filters: this.excludeUpcomingStatus(filters) });
    const findUpcomingInstances = this.service.findUpcomingInstances({
      ...filters,
      start_range: upInstanceStart.toISOString(),
      end_range: filters.start_range_end,
    });

    const shouldGetUpcomingInstances = (isToday(start) || isFutureDay(start)) || (!end || isToday(end) || isFutureDay(end));

    const req: CombinedResponse = [];

    if (filters.status?.length > 0) {

      if (filters.status.includes(InstanceStatus.Active)
        || filters.status.includes(InstanceStatus.Error)
        || filters.status.includes(InstanceStatus.Warning)
        || filters.status.includes(InstanceStatus.Completed)
      ) {
        req.push(findInstances);
      }

      if (filters.status.includes(InstanceStatus.Upcoming) && shouldGetUpcomingInstances) {
        req.push(findUpcomingInstances);
      }
    } else {
      req.push(findInstances);
      if (shouldGetUpcomingInstances) {
        req.push(findUpcomingInstances);
      }
    }

    return forkJoin(req).pipe(
      map(([ res1, res2 ]) => {
        const instanceOrUpcoming = res1.entities;
        const upcoming = res2?.entities ?? [];

        return [ ...instanceOrUpcoming, ...upcoming ];
      })
    );
  }

  @Reduce()
  onFindAllWithUpcoming(state: InstanceState, payload: (Instance | UpcomingInstance)[]): InstanceState {
    return { ...state, todayInstances: payload };
  }

  private excludeUpcomingStatus({ status, ...filters }: InstancesSearchFields) {
    return {
      ...filters,
      status: status?.filter((st) => st !== 'UPCOMING'),
    };
  }
}
