import { AfterContentInit, ChangeDetectionStrategy, Component, computed, ContentChild, ContentChildren, effect, ElementRef, Inject, Input, QueryList, Signal, signal, untracked, ViewChild, WritableSignal } from '@angular/core';
import { difference, OnHostResized } from '@observability-ui/core';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';
import { interval, SchedulerLike, startWith, Subject, switchMap } from 'rxjs';
import { GanttBarDirective } from './gantt-bar.directive';
import { GanttLabelDirective } from './gantt-label.directive';
import { toSignal } from '@angular/core/rxjs-interop';
import { GanttTaskGroup, Position } from './gantt-chart.model';

@Component({
  selector: 'gantt-chart',
  templateUrl: 'gantt-chart.component.html',
  styleUrls: [ 'gantt-chart.component.scss' ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GanttChartComponent implements AfterContentInit {
  @ViewChild('durations', { static: true }) private barsContainer!: ElementRef<HTMLDivElement>;

  @ContentChild(GanttLabelDirective) public labelTemplate!: GanttLabelDirective;
  @ContentChildren(GanttBarDirective) private taskTemplates!: QueryList<GanttBarDirective>;

  @Input()
  set start(value: Date) {
    this._dateRange.mutate(range => range.start = value);
  }

  @Input()
  set end(value: Date) {
    this._dateRange.mutate(range => range.end = value);
  }

  @Input() nowBar: boolean = false;

  @Input() set showDays(value: boolean) {
    this._showDays.set(value);
  }

  @Input() set timeformat(value: string) {
    this._timeformat.set(value ?? 'hh:mm a');
  }

  ticks: Signal<Array<{ format: string, time: Date }>> = computed(() => {
    const { start, end } = this._dateRange() as { start: Date; end: Date };
    if (!start || !end) {
      return [];
    }

    const format = this._timeformat();
    const showDays = this._showDays();

    const span = end.getTime() - start.getTime();
    const tickSpan = Math.floor(span / this.ticksCount);
    const extraTicks = Array(this.ticksCount).fill(0).map((_, idx) => new Date(start.getTime() + (idx * tickSpan)));
    const ticks = [ start, ...extraTicks.slice(1), end ].map(time => ({ format, time }));

    if (showDays) {
      ticks[0].format = `MMM d ${format}`;
      ticks[ticks.length - 1].format = `MMM d ${format}`;
    }

    return ticks;
  });

  now: Signal<{ offset: number; time: Date } | null> = computed(() => {
    this._resized();
    this._nowBarInterval();

    if (!this.nowBar) {
      return null;
    }

    const time = new Date();
    const { start, end } = this._dateRange() as { start: Date; end: Date };

    const width = this.barsContainer.nativeElement.clientWidth - 2;
    const chartStartTime = start.getTime();
    const chartTimeSpan = this.asTimeUnits(end.getTime() - chartStartTime);
    const tickSize = width / chartTimeSpan;

    const nowTimespan = this.asTimeUnits(time.getTime() - chartStartTime);
    const offset = nowTimespan * tickSize;

    return { offset, time };
  }, { equal: (a, b) => a?.time === b?.time });

  taskGroups: Signal<GanttTaskGroup[]> = computed(() => {
    this._regroup();

    const groups = new Map<string, GanttTaskGroup>();
    const groupChildren = new Map<string, Map<string, GanttTaskGroup>>();
    ;
    for (const taskSignal of this.tasksSignals.values()) {
      const task = taskSignal();

      const start_type = (task.ganttBarContext as any)?.start_type;
      const payload_key = (task.ganttBarContext as any)?.payload_key;

      if (!task.nested) {
        if (!groups.has(task.groupBy)) {
          groups.set(task.groupBy, {
            id: task.groupBy,
            start_type,
            payload_key,
            label: task.label,
            tasks: [],
            children: []
          });
        }
        groups.get(task.groupBy)?.tasks.push(task);
      } else {
        if (!groupChildren.has(task.parent!)) {
          groupChildren.set(task.parent!, new Map<string, GanttTaskGroup>());
        }
        const childGroup = groupChildren.get(task.parent!);
        if (!childGroup?.has(task.groupBy)) {
          childGroup?.set(task.groupBy, {
            id: task.groupBy,
            start_type,
            payload_key,
            label: task.label,
            tasks: [],
            children: []
          });
        }
        childGroup?.get(task.groupBy)?.tasks.push(task);
      }
    }

    const result: GanttTaskGroup[] = [];
    for (const group of groups.values()) {
      const children = Array.from(groupChildren.get(group.id)?.values() ?? []);
      result.push({ ...group, children });
    }
    return result;
  });

  private ticksCount: number = 4;
  private tasksSignals: Map<string, WritableSignal<GanttBarDirective>> = new Map<string, WritableSignal<GanttBarDirective>>();

  private _regroup: WritableSignal<number> = signal(0);
  private _resized: WritableSignal<number> = signal(0);
  private _showDays: WritableSignal<boolean> = signal(false);
  private _timeformat: WritableSignal<string> = signal('hh:mm a');
  private _dateRange: WritableSignal<{ start?: Date, end?: Date }> = signal({
    start: undefined,
    end: undefined
  }, { equal: (a, b) => a.start === b.start && a.end === b.end });
  private afterInit$ = new Subject<void>(); // NOTE: almost got rid of all the subjects but lifecycle hooks happened
  private _projectedTasks = toSignal<QueryList<GanttBarDirective>, QueryList<GanttBarDirective>>(
    this.afterInit$.pipe(
      switchMap(() =>
        this.taskTemplates.changes.pipe(
          startWith(this.taskTemplates),
        )
      ),
    ),
    { initialValue: new QueryList<GanttBarDirective>() }
  );

  private _nowBarInterval: Signal<number> = toSignal(interval(60000, this.scheduler), { initialValue: 0 });

  constructor(
    // ATTENTION! `element` is actually used by the OnHostResize observer
    private element: ElementRef,
    @Inject(rxjsScheduler) private scheduler: SchedulerLike,
  ) {
    effect(() => {
      this._resized();

      const { start, end } = this._dateRange() as { start: Date; end: Date };
      for (const taskSignal of this.tasksSignals.values()) {
        const task = taskSignal();
        const position = this.calculateTaskPositioning(start, end, task.start(), task.end());

        task.position = position ?? undefined;

        task.left.set(`${position?.offset ?? 0}px`);
        task.width.set(`${position?.duration ?? 0}px`);
        task.display.set(position ? 'inherit' : 'none');
      }
    }, { allowSignalWrites: true });

    effect(() => {
      const projectedTasks = this._projectedTasks();

      const currentTaskIds = new Set(this.tasksSignals.keys());
      const incomingTaskIds = new Set(projectedTasks.map(t => t.id));

      const addedTasks = difference(incomingTaskIds, currentTaskIds);
      const removedTasks = difference(currentTaskIds, incomingTaskIds);

      for (const task of projectedTasks) {
        if (addedTasks.has(task.id)) {
          this.tasksSignals.set(task.id, signal(task, { equal: this.areTasksEqual.bind(this) }));
        }
        this.tasksSignals.get(task.id)?.set(task);
      }

      for (const taskId of removedTasks) {
        this.tasksSignals.delete(taskId);
      }

      if ((addedTasks.size + removedTasks.size) > 0) {
        this._regroup.set(untracked(this._regroup) + 1);
        this._resized.set(untracked(this._resized) + 1);
      }
    }, { allowSignalWrites: true });
  }

  ngAfterContentInit(): void {
    this.afterInit$.next();
  }

  @OnHostResized()
  resizeTasks(): void {
    this._resized.set(this._resized() + 1);
  }

  private calculateTaskPositioning(chartStart: Date, chartEnd: Date, taskStart: Date, taskEnd: Date): Position | null {
    if (taskEnd < chartStart) {
      return null;
    }

    const tasksMinWidth = 5/*px*/;
    const bordersCompensation = 2; /* NOTE: The parent container does not account for each lanes border width */
    ;

    const width = this.barsContainer.nativeElement.clientWidth - bordersCompensation;
    const chartStartTime = chartStart.getTime();
    const taskStartTime = taskStart.getTime();
    const relativeTaskStart = Math.max(taskStartTime, chartStartTime);
    const chartTimeSpan = this.asTimeUnits(chartEnd.getTime() - chartStartTime);
    const taskOffset = this.asTimeUnits(taskStartTime - chartStartTime);
    const taskDuration = this.asTimeUnits(taskEnd.getTime() - relativeTaskStart);

    const tickSize = width / chartTimeSpan;
    const offset = Math.min(Math.max(taskOffset * tickSize, 0), width - tasksMinWidth);
    const duration = Math.min(taskDuration * tickSize, width);

    return { offset, duration };
  }

  private asTimeUnits(miliseconds: number): number {
    return miliseconds / 1000;
  }

  private areTasksEqual(taskA: GanttBarDirective, taskB: GanttBarDirective): boolean {
    return !!taskA
      && !!taskB
      && taskA.id === taskB.id
      && taskA.start().getTime() === taskB.start().getTime() && taskA.end().getTime() === taskB.end().getTime();
  }
}
