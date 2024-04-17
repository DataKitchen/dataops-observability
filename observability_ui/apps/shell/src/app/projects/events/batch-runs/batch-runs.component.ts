import { Component, OnInit } from '@angular/core';
import { beginningOfDay, endOfDay,  ProjectStore, RunProcessedStatus, toTimezoneAwareISOString } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup  } from '@datakitchen/ngx-toolkit';
import { BehaviorSubject, combineLatest, debounceTime, defer, map, merge, Subject, switchMap, takeUntil, tap } from 'rxjs';
import { RunsStore } from '../../../stores/runs/runs.store';
import { ComponentsService } from '../../../services/components/components.service';
import { ActivatedRoute } from '@angular/router';
import { TableChangeEvent } from '@observability-ui/ui';

interface SearchFields {
  pipeline_key: string;
  start_range_begin: string;
  start_range_end: string;
  status: string;
  tool: string;
  search: string;
}

@Component({
  selector: 'shell-batch-runs',
  templateUrl: 'batch-runs.component.html',
  styleUrls: [ 'batch-runs.component.scss' ],
})
export class BatchRunsComponent extends CoreComponent implements HasSearchForm<SearchFields>, OnInit {
  allPipelines$ = defer(() => this.currentProject$).pipe(
    switchMap(({ id: parentId }) => {
      return this.componentsService.findAll({ parentId });
    }),
    map(({ entities }) => {
      return entities
        .sort((a, b) => a.display_name?.localeCompare(b.display_name));
    })
  );

  readonly statusOptions: string[] = [
    RunProcessedStatus.Running.toString(),
    RunProcessedStatus.Completed.toString(),
    RunProcessedStatus.CompletedWithWarnings.toString(),
    RunProcessedStatus.Failed.toString(),
    RunProcessedStatus.Pending.toString(),
    RunProcessedStatus.Missing.toString(),
  ];

  now = new Date().getTime();
  runStatus = RunProcessedStatus;

  storageKey: string;

  runs$ = this.runsStore.list$;
  total$ = this.runsStore.total$;
  loading$ = merge(
    this.runsStore.getLoadingFor('getPage'),
    defer(() => this.antiFlickerLoading$.asObservable()),
  );

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<SearchFields>({
    pipeline_key: new TypedFormControl<string>(),
    start_range_begin: new TypedFormControl<string>(),
    start_range_end: new TypedFormControl<string>(),
    status: new TypedFormControl<string>(),
    tool: new TypedFormControl<string>(),
    search: new TypedFormControl<string>(),
  });

  search$ = new BehaviorSubject<SearchFields>({
    pipeline_key: '',
    start_range_begin: '',
    start_range_end: '',
    status: '',
    tool: '',
    search: '',
  });

  filtersApplied$ = this.search$.pipe(
    map(({ pipeline_key, start_range_begin, start_range_end, status, tool, search }) => !!pipeline_key || !!start_range_begin || !!start_range_end || !!status || !!tool || !!search),
  );
  antiFlickerLoading$ = new BehaviorSubject(true);

  private tableChange$ = new Subject<TableChangeEvent<SearchFields>>();
  private currentProject$ = this.projectStore.current$;

  constructor(
    storageService: StorageService,
    paramsService: ParameterService,
    private runsStore: RunsStore,
    private componentsService: ComponentsService,
    private route: ActivatedRoute,
    private projectStore: ProjectStore,
  ) {
    super(paramsService, storageService);
    this.storageKey = [ this.route.parent?.snapshot?.params['projectId'], 'PipelineRuns', '' ].join(':');
  }

  override ngOnInit(): void {

    combineLatest([
      this.tableChange$.pipe(
        map(({ search, ...page }) => {
          return {
            ...page,
            search: this.remapSearchFields(search)
          };
        })
      ),
      this.currentProject$,
    ]).pipe(
      debounceTime(this.defaultDebounce + 20, this.scheduler),
      takeUntil(this.destroyed$),
    ).subscribe(([ {
      pageIndex: page,
      pageSize: count,
      search: filters
    }, project ]) => {
      this.runsStore.dispatch('getPage', {
        page,
        count,
        filters,
        sort: 'desc',
        parentId: project.id,
      });

      this.search$.pipe(
        tap(() => this.antiFlickerLoading$.next(true)),
        takeUntil(this.destroyed$),
      ).subscribe();
    });

    super.ngOnInit();
  }

  onTableChange(page: TableChangeEvent<SearchFields>) {
    this.tableChange$.next(page);
  }

  remapSearchFields({ pipeline_key, start_range_begin, start_range_end, status, tool, search }: SearchFields) {
    const fields = {
      pipeline_key: pipeline_key?.split(',')?.filter(n => n) || [],
      start_range_begin: '',
      start_range_end: '',
      status: status?.split(',').filter((e: string) => e) || [],
      tool: tool?.split(',').filter((e: string) => e) || [],
      search: search?.trim(),
    };

    if (start_range_begin) {
      const startDate = beginningOfDay(new Date(start_range_begin));
      fields.start_range_begin = toTimezoneAwareISOString(startDate);
    }

    if (start_range_end) {
      const endDate = endOfDay(new Date(start_range_end));
      fields.start_range_end = toTimezoneAwareISOString(endDate);
    }

    return fields;
  }
}
