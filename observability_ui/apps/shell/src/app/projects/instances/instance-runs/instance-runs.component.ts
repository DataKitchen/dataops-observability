import { Component, OnInit } from '@angular/core';
import { BehaviorSubject, distinctUntilChanged, filter, map, startWith, Subject, switchMap, takeUntil, tap, withLatestFrom } from 'rxjs';
import { TableChangeEvent } from '@observability-ui/ui';
import { ProjectStore, RunProcessedStatus } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, StorageService, TypedFormControl, TypedFormGroup, Prop } from '@datakitchen/ngx-toolkit';
import { ActivatedRoute } from '@angular/router';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { RunsStore } from '../../../stores/runs/runs.store';

interface SearchFields {
  component_id: string;
  status: RunProcessedStatus|undefined;
  tool: string;
  search: string;
}

@Component({
  selector: 'shell-instance-runs',
  templateUrl: 'instance-runs.component.html',
  styleUrls: [ 'instance-runs.component.scss' ],
})

export class InstanceRunsComponent extends CoreComponent implements OnInit, HasSearchForm<SearchFields> {
  runs$ = this.runsStore.list$;
  loading$ = this.runsStore.getLoadingFor('getPage').pipe(
    startWith(true)
  );
  total$ = this.runsStore.total$;

  allComponents$ = this.store.components$.pipe(
    map(components => components.sort((a, b) => a.display_name.localeCompare(b.display_name))),
  );

  readonly statusOptions: string[] = [
    RunProcessedStatus.Running.toString(),
    RunProcessedStatus.Completed.toString(),
    RunProcessedStatus.CompletedWithWarnings.toString(),
    RunProcessedStatus.Failed.toString(),
    RunProcessedStatus.Pending.toString(),
    RunProcessedStatus.Missing.toString(),
  ];

  storageKey!: string;

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<SearchFields>({
    component_id: new TypedFormControl<string>(),
    status: new TypedFormControl<RunProcessedStatus|undefined>(),
    tool: new TypedFormControl<string>(),
    search: new TypedFormControl<string>(),
  });

  search$: BehaviorSubject<SearchFields> = new BehaviorSubject<SearchFields>({ component_id: '', status: undefined, tool: '', search: '' });

  private tableChange$: Subject<TableChangeEvent> = new Subject<TableChangeEvent>();

  constructor(
    storageService: StorageService,
    paramsService: ParameterService,
    private route: ActivatedRoute,
    private store: InstancesStore,
    private runsStore: RunsStore,
    private projectStore: ProjectStore,
  ) {
    super(paramsService, storageService);
  }

  override ngOnInit() {
    const projectId$ = this.projectStore.current$.pipe(
      map(({ id }) => id),
    );
    const instanceId$ = this.route.parent!.params.pipe(
      map(({ id }) => id as string),
    );

    instanceId$.pipe(
      tap((instanceId) => this.storageKey = [ instanceId, 'InstanceRuns', '' ].join(':')),
      tap((instanceId) => this.store.dispatch('getOne', instanceId)),
      switchMap((instanceId) => this.store.getEntity(instanceId)),
      filter((instance) => !!instance),
      distinctUntilChanged((prev, curr) => prev?.id === curr?.id),
      takeUntil(this.destroyed$),
    ).subscribe((instance) => {
      this.store.dispatch('findComponents', instance!.journey.id);
    });

    this.tableChange$.pipe(
      withLatestFrom(projectId$, instanceId$, this.allComponents$),
      takeUntil(this.destroyed$),
    ).subscribe(([ { search: { component_id, status, tool, search }, pageIndex, pageSize }, parentId, instanceId, componentOptions ]) => {
      const pipelines = component_id?.split(',').filter((t: string) => t) || [];

      this.runsStore.dispatch('getPage', {
        parentId,
        sort: 'desc',
        page: pageIndex,
        count: pageSize,
        filters: {
          instance_id: instanceId,
          status: status?.split(',').filter((e: string) => e) || [],
          pipeline_id: pipelines.length === componentOptions.length ? [] : pipelines,
          tool: tool?.split(',').filter((e: string) => e) || [],
          search: search?.trim(),
        },
      });

      this.store.dispatch('getOne', instanceId);
    });

    super.ngOnInit();
  }

  onTableChange(page: TableChangeEvent<SearchFields>) {
    this.tableChange$.next(page);
  }
}
