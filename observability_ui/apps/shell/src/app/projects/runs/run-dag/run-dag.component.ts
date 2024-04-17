import { Component, OnDestroy, OnInit, effect, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject, combineLatest, map, Subject, takeUntil, tap } from 'rxjs';
import { parseDate, RunTask } from '@observability-ui/core';
import { StorageService } from '@datakitchen/ngx-toolkit';
import { RunTasksStore } from '../../../stores/run-tasks/run-tasks.store';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RunsStore } from '../../../stores/runs/runs.store';

@Component({
  selector: 'shell-run-dag',
  templateUrl: 'run-dag.component.html',
  styleUrls: [ 'run-dag.component.scss' ]
})
export class RunDagComponent implements OnInit, OnDestroy {
  tasks$ = this.store.list$.pipe(
    map(tasks =>
      tasks.map(t => ({
        ...t,
        start_time: parseDate(t.start_time)!,
        end_time: parseDate(t.end_time as string)!
      }))
    ),
    tap(tasks => this.handleError(tasks.length <= 0 ? 'No tasks found' : undefined)),
  );

  edges$ = this.tasks$.pipe(
    map(tasks => this.linkTasks(tasks)),
  );

  loading$ = this.store.getLoadingFor('findAll');

  error$ = new BehaviorSubject<string | undefined>(undefined);

  showEdges = signal<boolean>(true);

  private refresh$: BehaviorSubject<void> = new BehaviorSubject<void>(undefined);
  private destroyed$: Subject<void> = new Subject<void>();
  private StorageNamespace = 'RunDag:Edges:';

  constructor(
    storage: StorageService,
    private store: RunTasksStore,
    private runStore: RunsStore,
    private route: ActivatedRoute,
  ) {

    effect(() => {
      const runId = this.route.parent!.snapshot.params['runId'];
      storage.setStorage(this.StorageNamespace + runId, this.showEdges());
    });

    this.route.parent!.params.pipe(
      map(({ runId }) => runId),
      takeUntilDestroyed(),
    ).subscribe((runId) => {
      const edgesShown = storage.getStorage(this.StorageNamespace + runId) as boolean;
      if (edgesShown !== null && edgesShown !== undefined) {
        this.showEdges.set(edgesShown);
      }
    });
  }

  ngOnInit(): void {

    combineLatest([
      this.route.parent!.params.pipe(
        map(({ runId }) => runId),
      ),
      this.refresh$,
    ]).pipe(
      takeUntil(this.destroyed$)
    ).subscribe(([ parentId ]) => {
      this.store.dispatch('findAll', { parentId });
      this.runStore.dispatch('getOne', parentId);
    });

  }

  handleError(message: string | undefined): void {
    this.error$.next(message);
  }

  refresh(): void {
    this.refresh$.next();
  }

  linkTasks(tasks: Array<Omit<RunTask, 'start_time' | 'end_time'> & { start_time: Date, end_time?: Date }>): Array<{ from: RunTask['id'], to: RunTask['id'] }> {
    const currentTime = new Date();

    const edges: Array<{ from: RunTask['id'], to: RunTask['id'] }> = [];
    const sortedTasks = tasks
      .map(t => ({ ...t, end_time: t.end_time || currentTime }))
      .sort((taskA, taskB) => {
        if (taskA.start_time === taskB.start_time) {
          return this.sortAscending(taskA.end_time, taskB.end_time);
        }
        return this.sortAscending(taskA.start_time, taskB.start_time);
      });

    for (const [ index, taskA ] of sortedTasks.entries()) {
      let lastTaskEndTime: Date | undefined;
      for (const taskB of sortedTasks.slice(index + 1)) {
        if (lastTaskEndTime && taskB.start_time >= lastTaskEndTime) { // Task B starts after a task already connected to Task A
          break; // No need to check remaining nodes since they are sorted
        } else if (taskB.start_time >= taskA.end_time && taskB.start_time > taskA.start_time) {
          edges.push({ from: taskA.id, to: taskB.id });
          // lastTaskEndTime = taskB.end_time;
          lastTaskEndTime = lastTaskEndTime ? this.earlierDate(lastTaskEndTime, taskB.end_time) : taskB.end_time;
        }
      }
    }

    return edges;
  }

  private sortAscending(a: Date, b: Date): number {
    return a.valueOf() - b.valueOf();
  }

  private earlierDate(a: Date, b: Date): Date {
    return (a.valueOf() - b.valueOf()) <= 0 ? a : b;
  }

  toggleEdgesVisibility(): void {
    this.showEdges.set(!this.showEdges());
  }

  ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
  }
}
