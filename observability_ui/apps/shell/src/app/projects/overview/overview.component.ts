import { Component, OnDestroy, OnInit, Signal } from '@angular/core';
import { combineLatest, debounceTime, defer, distinctUntilChanged, filter, first, map, merge, Observable, of, pairwise, repeat, skip, startWith, takeUntil, timer, withLatestFrom } from 'rxjs';
import { BindToQueryParams, CoreComponent, ParameterService } from '@datakitchen/ngx-toolkit';
import { isSameDay, parseDate, parseInstances, ProjectStore, Run, RunProcessedStatus, TodayInstance } from '@observability-ui/core';
import { InstancesStore } from '../../stores/instances/instances.store';
import { FormControl, FormGroup } from '@angular/forms';
import { JourneysStore } from '../journeys/journeys.store';
import { DotsChartLevel, GanttBarDirective } from '@observability-ui/ui';
import { tap } from 'rxjs/operators';
import { toSignal } from '@angular/core/rxjs-interop';

type TodayRun = Omit<Run, 'start_time' | 'end_time'> & { start_time: Date; end_time: Date; hasTime: boolean };

@Component({
  selector: 'shell-project-overview',
  templateUrl: 'overview.component.html',
  styleUrls: [ './overview.component.scss' ]
})
export class ProjectOverviewComponent extends CoreComponent implements OnInit, OnDestroy {

  @BindToQueryParams()
  form: FormGroup<{ day: FormControl<string>, journey: FormControl<string> }> = new FormGroup({
    day: new FormControl() as FormControl<string>,
    journey: new FormControl() as FormControl<string>
  });

  /* istanbul ignore next */
  private displayDayChanges$ = defer(() => {
    return this.form.controls.day.valueChanges.pipe(
      startWith(this.form.value.day ?? new Date().toISOString()),
    );
  }).pipe(
    map((day) => new Date(day)),
    map((day) => new Date(day.setHours(0, 0, 0))),
  );

  shouldDisplayLoading = toSignal(merge(
    of([ true, true, true ]),
    combineLatest([
      this.store.getLoadingFor('getDayInstances').pipe(
        first(loading => !loading),
      ),
      this.projectStore.getLoadingFor('getEventsByPage').pipe(
        first(loading => !loading),
      ),
      this.journeyStore.getLoadingFor('findAll').pipe(
        first(loading => !loading),
      ),
    ])
  ).pipe(
    map(([ instanceLoading, eventsLoading, journeysLoading ]) => instanceLoading || eventsLoading || journeysLoading),
    repeat({
      delay: () => this.projectStore.current$.pipe(
        distinctUntilChanged((previous, current) => previous?.id === current?.id),
        skip(1),
      )
    }),
  ));

  projectId!: string;

  /* istanbul ignore next */
  journeysFilter$ = this.form.controls.journey.valueChanges.pipe(
    startWith(this.form.controls.journey.value ?? ''),
  );

  totalEvents$ = this.projectStore.totalEvents$;

  isToday$ = this.displayDayChanges$.pipe(
    map((day) => isSameDay(day, new Date())),
  );

  /* istanbul ignore next */
  now$ = timer(0, 60000, this.scheduler).pipe(
    map(() => new Date()),
    filter((now) => isSameDay(now, this.form.value.day ? new Date(this.form.value.day as string) : new Date())),
    startWith(new Date()),
  );

  instances$: Observable<TodayInstance[]> = this.store.todayInstances$.pipe(
    withLatestFrom(this.now$, this.displayDayChanges$),
    map(([ instances, now ]) => {
      return instances
        .map((instance) => parseInstances(instance, now))
        .sort((a, b) => {
          return a.journey.name.localeCompare(b.journey.name);
        });
    })
  );

  instanceRuns$: Observable<TodayRun[]> = this.store.runs$.pipe(
    filter(() => !!this.expandedDate),
    map((runs) =>
      runs.map((run) => {
        const instanceStartTime = this.expandedDate.instances.map(i => i.start_time).filter(t => t).reduce((a, b) => a < b ? a : b);
        const instanceEndTime = this.expandedDate.instances.map(i => i.end_time).filter(t => t).reduce((a, b) => a > b ? a : b);

        const start_time = parseDate(run.start_time) ?? instanceStartTime;
        const end_time = parseDate(run.end_time) ?? instanceEndTime;

        return {
          ...run,
          hasTime: ![ RunProcessedStatus.Missing, RunProcessedStatus.Pending ].includes(run.status),
          start_time,
          end_time
        };
      }).sort((a, b) => a.start_time!.getTime() - b.start_time!.getTime())
    )
  );

  private today$ = merge(
    this.now$,
    this.displayDayChanges$,
  ).pipe(
    pairwise(),
    filter(([ prev, curr ]) => !isSameDay(prev, curr)),
    map(([ , today ]) => today),
  );

  ganttStartDate$ = this.today$.pipe(
    startWith(new Date()),
    map((today) => new Date(today.setHours(0, 0, 0))),
  );

  ganttEndDate$ = this.today$.pipe(
    startWith(new Date()),
    map((today) => new Date(today.setHours(23, 59, 59))),
  );

  loading: Signal<boolean> = toSignal(this.store.getLoadingFor('getDayInstances'));

  journeys$ = this.journeyStore.list$;

  expandedDate: { id: string; instances: TodayInstance[] } | null = null;

  currentProject$ = this.projectStore.current$;

  chartLevels: DotsChartLevel[] = [
    {
      groupByField: 'journey.id',
      labelField: 'journey.name',
      linkField: this.journeyLink,
    },
    {
      groupByField: this.instanceFormattedDate,
      labelField: this.instanceFormattedDate,
      external: true
    }
  ];

  constructor(
    private store: InstancesStore,
    private projectStore: ProjectStore,
    private journeyStore: JourneysStore,
    paramsService?: ParameterService,
  ) {
    super(paramsService);
  }

  override ngOnInit(): void {


    combineLatest([
      this.currentProject$,
      this.displayDayChanges$,
      this.journeysFilter$,
      // journeyFilter$ is bound to the form which is `@BoundToQueryParams`
      // @BindToQueryParams is unidirectional, meaning that when the form changes
      // it updates the query params the other way round doesn't happen
      // hence when navigating to a new project while in the project overview page
      // while the url gets cleaned it's not the same for the journeyFilter which
      // still holds the previous value.
      this.projectStore.projectChanged$.pipe(
        tap((changed) => {
          // when the current project changes
          if (changed) {
            this.form.patchValue({ journey: null });
          }
        }),
      ),
      this.now$,
    ]).pipe(
      debounceTime(100, this.scheduler),
      takeUntil(this.destroyed$),
    ).subscribe(([ project, date, journeys ]) => {
      // subscription 👆 must happen before `super.ngOnInit()`
      // otherwise first value change will be lost

      if (project.id !== this.projectId) {
        this.projectStore.dispatch('getEventsByPage', { parentId: project.id, count: 0 });
      }

      this.projectId = project.id;
      this.journeyStore.dispatch('findAll', { parentId: project.id });

      // so when the project changes we want to just disregard the current value in form.journey
      const journey_ids = (journeys as string)?.split(',')?.filter(n => n) ?? [];
      this.store.dispatch('getDayInstances', { parentId: project.id }, date, journey_ids);
      if (this.expandedDate) {
        this.store.dispatch('getDayInstanceRuns', project.id, this.expandedDate.instances.map(i => i.id), date);
      }
    });

    super.ngOnInit();
  }

  expandDate(id: string, tasks: GanttBarDirective[]): void {
    const today = new Date();
    const instances = tasks.map(t => t.context as TodayInstance);

    this.collapseDate();
    this.expandedDate = { id, instances };
    this.store.dispatch('getDayInstanceRuns', this.projectId, instances.map(i => i.id), new Date(this.form.value.day ?? today.toISOString()));
  }

  collapseDate(): void {
    this.expandedDate = null;
    this.store.dispatch('clearBatchRuns');
  }

  instanceDotsTrackBy(_: number, instance: TodayInstance): string {
    return `${instance.id}-${instance.journey.name}-${instance.status}-${instance.start_time}-${instance.end_time}`;
  }

  instanceGanttTrackBy(_: number, { value: instance }: { value: TodayInstance }): string {
    return `${instance.id}-${instance.journey.name}-${instance.status}-${instance.start_time}-${instance.end_time}`;
  }

  runTrackBy(_: number, run: Run): string {
    return `${run.id}-${run.pipeline.display_name}-${run.status}-${run.start_time}-${run.end_time}`;
  }

  today(): void {
    this.form.patchValue({ day: new Date().toISOString() });
  }

  previousDate(): void {
    const today = new Date();
    const currentDayInMillis = new Date(this.form.value.day ?? today.toISOString()).getTime();
    this.form.patchValue({ day: new Date(currentDayInMillis - 1 * 24 * 60 * 60 * 1000).toISOString() });
  }

  nextDate(): void {
    const today = new Date();
    const currentDay = new Date(this.form.value.day ?? today.toISOString());


    this.form.patchValue({ day: new Date(currentDay.getTime() + 1 * 24 * 60 * 60 * 1000).toISOString() });
  }

  instanceFormattedDate(instance: TodayInstance): string {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    }).format(instance.start_time);
  }

  journeyLink(instance: TodayInstance): string {
    if (!instance.project || !instance.journey) {
      return '';
    }

    return `/projects/${instance.project.id}/journeys/${instance.journey.id}`;
  }

}
