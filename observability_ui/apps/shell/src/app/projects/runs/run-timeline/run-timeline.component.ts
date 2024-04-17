import { Component, OnDestroy, OnInit } from '@angular/core';
import { RunTasksStore } from '../../../stores/run-tasks/run-tasks.store';
import { ActivatedRoute, Router } from '@angular/router';
import { max, min, parseDate, RunProcessedStatus, RunTask } from '@observability-ui/core';
import { combineLatest, filter, map, Observable, startWith, Subscription, switchMap, takeUntil, timer, withLatestFrom } from 'rxjs';
import { Overwrite } from 'utility-types';
import { RunsStore } from '../../../stores/runs/runs.store';

type RunTaskUI = Overwrite<RunTask, {
  start_time: Date|undefined;
  end_time: Date|null|undefined;
}> & {hasTime: boolean};

@Component({
  selector: 'shell-run-timeline',
  templateUrl: 'run-timeline.component.html',
  styleUrls: [ 'run-timeline.component.scss' ]
})
export class RunTimelineComponent implements OnInit, OnDestroy {
  run$ = this.route.parent!.params.pipe(
    map(({ runId }) => runId),
    switchMap((runId) => this.runStore.getOne(runId)),
  );
  runIsRunning$ = this.run$.pipe(
    map((run) => run.status === RunProcessedStatus.Running),
  );

  tasks$: Observable<RunTaskUI[]> = this.store.list$.pipe(
    map((tasks) => {
      return tasks.map((task) => {
        return {
          ...task,
          start_time: parseDate(task.start_time),
          end_time: task.end_time ? parseDate(task.end_time) : new Date(),
          hasTime: ![ RunProcessedStatus.Missing, RunProcessedStatus.Pending ].includes(task.status),
        };
      }).sort((a, b) => a.start_time!.getTime() - b.start_time!.getTime());
    }),
  );
  loading$ = this.store.getLoadingFor('findAll');

  ganttStartDate$ = this.tasks$.pipe(
    min((a, b) => a.start_time!.getTime() - b.start_time!.getTime(), () => ({start_time: new Date()} as RunTaskUI)),
    map((task) => task.start_time!),
  );
  ganttEndDate$ = this.tasks$.pipe(
    max((a, b) => a.end_time!.getTime() - b.end_time!.getTime(), () => ({end_time: new Date()} as RunTaskUI)),
    map((task) => task.end_time!),
    withLatestFrom(this.ganttStartDate$),
    map(([ endDate, startDate ]) => {
      let end = endDate;
      const timespan = endDate.getTime() - startDate.getTime();
      if (timespan < this.minTimespanInMilliseconds) {
        end = new Date(startDate.getTime() + this.minTimespanInMilliseconds);
      }
      return end;
    }),
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

  private subscriptions: Subscription[] = [];
  private minTimespanInMilliseconds: number = 1 * 60 * 1000;

  constructor(
    private store: RunTasksStore,
    private runStore: RunsStore,
    private route: ActivatedRoute,
    private router: Router) {}

  ngOnInit(): void {
    const runStoppedRunning$ = this.runIsRunning$.pipe(
      filter((isRunning) => !isRunning),
    );

    const sub = combineLatest([
      this.run$,
      timer(0, 60 * 1000).pipe(
        takeUntil(runStoppedRunning$),
        startWith(''),
      ),
    ]).subscribe(([ run ]) => {
      this.store.dispatch('findAll', { parentId: run.id });
      this.runStore.dispatch('getOne', run.id);
    });

    this.subscriptions.push(sub);
  }

  ngOnDestroy() {
    this.subscriptions.forEach((sub) => sub.unsubscribe());
  }
}
