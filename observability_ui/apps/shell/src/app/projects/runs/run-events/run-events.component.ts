import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TableChangeEvent } from '@observability-ui/ui';
import { BehaviorSubject, combineLatest, map, startWith, Subject, takeUntil, tap } from 'rxjs';
import { EventSearchFields, EventTypes, ProjectStore } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { RunTasksStore } from '../../../stores/run-tasks/run-tasks.store';
import { RunsStore } from '../../../stores/runs/runs.store';


@Component({
  selector: 'shell-run-events',
  templateUrl: './run-events.component.html',
  styleUrls: [ './run-events.component.scss' ]
})
export class RunEventsComponent extends CoreComponent implements OnInit, HasSearchForm<EventSearchFields> {
  events$ = this.projectStore.events$;
  allTasks$ = this.runTasksStore.list$.pipe(
    map(tasks => tasks.sort((a, b) => a.task.display_name.localeCompare(b.task.display_name))),
  );

  total$ = this.projectStore.totalEvents$;
  loading$ = this.projectStore.getLoadingFor('getEventsByPage').pipe(
    startWith(true)
  );

  storageKey!: string;

  readonly events = EventTypes;

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<EventSearchFields>({
    task_id: new TypedFormControl<string>(),
    event_type: new TypedFormControl<string>(),
  });

  search$: BehaviorSubject<EventSearchFields> = new BehaviorSubject<EventSearchFields>({
    task_id: '',
    event_type: ''
  });

  private tableChange$ = new Subject<TableChangeEvent<EventSearchFields>>();

  constructor(
    paramService: ParameterService,
    storageService: StorageService,
    private route: ActivatedRoute,
    private runTasksStore: RunTasksStore,
    private runStore: RunsStore,
    private projectStore: ProjectStore,
  ) {
    super(paramService, storageService);
  }

  override ngOnInit(): void {

    this.route.parent?.params.pipe(
      tap(({ runId, projectId }) => {
        this.storageKey = [ projectId, 'RunEvents', runId ].join(':');
        this.runTasksStore.dispatch('findAll', { parentId: runId });
      })
    ).subscribe();

    combineLatest([
      this.projectStore.current$.pipe(map(({ id }) => id)),
      // If we do not have the runId this component can't even start
      // so it is safe to disable the following rule assuming that parent route
      // is always available
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      this.route.parent!.params.pipe(
        map(({ runId }) => runId),
      ),
      this.tableChange$,
      this.allTasks$,
    ]).pipe(
      takeUntil(this.destroyed$),
    ).subscribe(([ projectId, runId, {
      search: { event_type, task_id },
      pageIndex,
      pageSize
    }, taskOptions ]) => {

      const tasks = task_id?.split(',').filter((t: string) => t) || [];
      const eventTypes = event_type?.split(',').filter((e: string) => e) || [];

      this.projectStore.dispatch('getEventsByPage', {
        parentId: projectId,
        sort: 'desc',
        page: pageIndex,
        count: pageSize,
        filters: {
          run_id: runId,
          task_id: tasks.length === taskOptions.length ? [] : tasks as any,
          event_type: eventTypes as any,
        },
      });

      this.runStore.dispatch('getOne', runId);
    });

    super.ngOnInit();
  }

  onTableChange(page: TableChangeEvent<EventSearchFields>) {
    this.tableChange$.next(page);
  }
}
