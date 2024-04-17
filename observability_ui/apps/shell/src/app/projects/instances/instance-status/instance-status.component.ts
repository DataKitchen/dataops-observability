import { ChangeDetectorRef, Component, signal, WritableSignal } from '@angular/core';
import { ComponentType, InstanceDagNode, JourneyDagEdge, RunProcessedStatus } from '@observability-ui/core';
import { combineLatest, concatMap, filter, from, mergeMap, of, timer } from 'rxjs';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { distinctUntilChanged, map, tap } from 'rxjs/operators';
import { DagStore } from '../../../stores/dag/dag.store';

@Component({
  selector: 'shell-instance-status',
  templateUrl: 'instance-status.component.html',
  styleUrls: [ 'instance-status.component.scss' ],
  providers: [ DagStore ]
})
export class InstanceStatusComponent {
  outOfSequenceAlert = toSignal(this.instanceStore.outOfSequenceAlert$);

  error: WritableSignal<string | undefined> = signal<string | undefined>(undefined);

  runStatus = RunProcessedStatus;
  componentType = ComponentType;
  nodes$ = this.store.nodes$;
  edges$ = this.store.edges$;

  projectId = toSignal(this.instanceStore.selected$.pipe(
    map(({project}) => project.id)
  ));

  journeyId = toSignal(this.instanceStore.selected$.pipe(
    map(({journey}) => journey.id)
  ));

  constructor(
    private store: DagStore,
    private instanceStore: InstancesStore,
    private changeDetectorRef: ChangeDetectorRef
  ) {
    this.instanceStore.selected$.pipe(
      tap((instance) => {
        if (instance) {
          this.store.dispatch('getDag', instance.journey.id);
          this.instanceStore.dispatch('getOutOfSequenceAlert', instance.project.id, instance.id);
          this.instanceStore.dispatch('getOne', instance.id);
        }
      }),
      takeUntilDestroyed(),
    ).subscribe();

    combineLatest([
      this.store.nodes$.pipe(
        filter((nodes) => nodes?.length > 0),
        distinctUntilChanged((previous, current) => {
          return previous.length === current.length;
        }),
        concatMap((nodes) => {
          return from(nodes).pipe(
            concatMap((value) =>
              timer(400).pipe(
                mergeMap(() => of(value)),
              )
            )
          );
        }),
      ),
      this.instanceStore.selected$,
    ]).pipe(
      takeUntilDestroyed(),
    ).subscribe(([ node, instance ]) => {
      if (instance) {
        this.store.dispatch('getDagNodeDetail', instance.project.id, instance.id, node.info);
        this.changeDetectorRef.markForCheck();
      }
    });
  }

  handleError(message: string | undefined): void {
    this.error.set(message);
  }

  resetError(): void {
    this.error.set(undefined);
  }

  nodeTrackByFn(_: number, node: { info: InstanceDagNode }): string {
    return node.info.component.id;
  }

  edgeTrackByFn(_: number, edge: JourneyDagEdge): string {
    return edge.id;
  }
}
