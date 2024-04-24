import { Injectable } from '@angular/core';
import { EntityActions, EntityListResponse, EntityState, EntityStore, PaginatedRequest, Pagination, ProjectService, Run, SortOptions, TestOutcomeItem, TestsSearchFields } from '@observability-ui/core';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { ProjectRunsService } from '../../services/project-runs/project-runs.service';
import { map, Observable } from 'rxjs';

export interface RunsActions extends EntityActions<Run> {
  getTestsByPage: (projectId: string, req: PaginatedRequest<TestsSearchFields>) => Observable<EntityListResponse<TestOutcomeItem> & Pagination & SortOptions>;
}

interface RunsState extends EntityState<Run> {
  tests: EntityState<TestOutcomeItem>;
}

@Injectable({
  providedIn: 'root'
})
export class RunsStore extends EntityStore<RunsState, RunsActions> implements makeStore<RunsState, RunsActions> {
  tests$ = this.select(({ tests }) => tests.list);
  testsTotal$ = this.select(({ tests }) => tests.total);

  constructor(protected service: ProjectRunsService, private projectService: ProjectService,) {
    super({
      total: 0,
      list: [],
      tests: {
        list: [],
        total: 0,
      },
    });
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
  onGetTestsByPage(state: RunsState, {
    entities,
    total,
    page,
    count,
    sort
  }: EntityListResponse<TestOutcomeItem> & Pagination & SortOptions): RunsState {
    return { ...state, tests: { list: entities, total, page, count, sort } };
  }
}
