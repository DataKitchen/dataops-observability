import { Component, OnDestroy, OnInit } from '@angular/core';
import { max, min, parseDate, ProjectStore, Run, RunProcessedStatus } from '@observability-ui/core';
import { ActivatedRoute } from '@angular/router';
import { combineLatest, defer, distinctUntilChanged, map, Observable, startWith, Subscription, takeUntil, timer, withLatestFrom } from 'rxjs';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { Overwrite } from 'utility-types';

type TimelineRun = Overwrite<Run, {start_time: Date; end_time: Date}> & {hasTime: boolean};

@Component({
  selector: 'shell-instance-timeline',
  templateUrl: './instance-timeline.component.html',
  styleUrls: [ 'instance-timeline.component.scss' ]
})
export class InstanceTimelineComponent implements OnInit, OnDestroy {
  parentId: string;
  subscriptions: Subscription[] = [];

  instance$ = defer(() => this.store.getOne(this.parentId));
  instanceIsActive$ = this.instance$.pipe(
    map((instance) => instance.active),
  );

  runs$: Observable<TimelineRun[]> = this.store.runs$.pipe(
    map((runs) => {
      return runs.map((run) => ({
        ...run,
        start_time: parseDate(run.start_time) ?? new Date(), // TODO: Use a default start somehow
        end_time: parseDate(run.end_time) ?? new Date(),
        hasTime: ![ RunProcessedStatus.Missing, RunProcessedStatus.Pending ].includes(run.status),
      })).sort((a, b) => a.start_time!.getTime() - b.start_time!.getTime());
    }),
  );
  loading$ = this.store.getLoadingFor('findAllBachRuns');

  ganttStartDate$ = this.runs$.pipe(
    min((a, b) => a.start_time!.getTime() - b.start_time!.getTime(), () => ({start_time: new Date()} as TimelineRun)),
    map((run) => run.start_time!),
    distinctUntilChanged(),
  );
  ganttEndDate$ = this.runs$.pipe(
    max((a, b) => a.end_time.getTime() - b.end_time.getTime(), () => ({end_time: new Date()} as TimelineRun)),
    map((run) => run.end_time!),
    withLatestFrom(this.ganttStartDate$),
    map(([ endDate, startDate ]) => {
      let end = endDate;
      const timespan = endDate.getTime() - startDate.getTime();
      if (timespan < this.minTimespanInMilliseconds) {
        end = new Date(startDate.getTime() + this.minTimespanInMilliseconds);
      }
      return end;
    }),
    distinctUntilChanged(),
  );
  timeformat$ = combineLatest([ this.ganttStartDate$, this.ganttEndDate$ ]).pipe(
    map(([ start, end ]) => {
      const timespan = end.getTime() - start.getTime();
      if (timespan <= this.minTimespanInMilliseconds) {
        return 'hh:mm:ss a';
      }
      return 'hh:mm a';
    }),
    startWith('hh:mm a'),
  );
  spansMultipleDays$ = combineLatest([ this.ganttStartDate$, this.ganttEndDate$ ]).pipe(
    map(([ start, end ]) => {
      return (end.getTime() - start.getTime()) > 24 * 60 * 60 * 1000;
    }),
  );

  private minTimespanInMilliseconds: number = 1 * 60 * 1000;
  constructor(
    private route: ActivatedRoute,
    private store: InstancesStore,
    private projectStore: ProjectStore,
  ) {
    this.parentId = this.route.snapshot.parent?.params['id'];
  }

  ngOnInit() {
    const instanceIsInactive$ = this.instanceIsActive$.pipe(
      map((isActive) => !isActive),
    );
    const projectId$ = this.projectStore.current$.pipe(
      map(({ id }) => id),
    );
    const instanceId$ = this.route.parent!.params.pipe(
      map(({ id }) => id as string),
    );

    this.subscriptions.push(
      combineLatest([
        projectId$,
        instanceId$,
        timer(0, 60 * 1000).pipe(
          takeUntil(instanceIsInactive$),
          startWith(''),
        ),
      ]).subscribe(([ projectId, instanceId ]) => {
        this.store.dispatch('findAllBachRuns', projectId, instanceId);
        this.store.dispatch('getOne', instanceId);
      })
    );
  }

  ngOnDestroy() {
    this.store.dispatch('clearBatchRuns');
    this.subscriptions.forEach((sub) => sub.unsubscribe());
  }
}
