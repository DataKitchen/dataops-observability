import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { BaseComponent, JourneyDagEdge, ProjectStore } from '@observability-ui/core';
import { DagComponent, DagEdgeDirective, DagNodeDirective } from '@observability-ui/ui';
import { BehaviorSubject, Observable, combineLatest, debounceTime, filter, map, startWith } from 'rxjs';
import { DagCompleteNode, DagStore } from '../../../stores/dag/dag.store';
import { MatLegacyCheckbox } from '@angular/material/legacy-checkbox';

@Component({
  selector: 'shell-journey-relationships',
  templateUrl: 'journey-relationships.component.html',
  styleUrls: [ 'journey-relationships.component.scss' ],
  providers: [DagStore]
})
export class JourneyRelationshipsComponent {
  @ViewChild(DagComponent, { static: true, read: ElementRef }) dagEl: ElementRef;

  nodes$ = this.store.nodes$;

  edges$ = this.store.edges$;

  components$ = this.store.components$;
  componentsInDag$ = this.store.componentsInDag$;

  canDelete$ = this.store.canDelete$;

  loadingDag$ = this.store.getLoadingFor('getDag').pipe(
    startWith(true),
  );

  loadingComponents$ = this.store.getLoadingFor('getComponents').pipe(
    startWith(true),
  );

  error$ = new BehaviorSubject<string | undefined>(undefined);

  projectId: string;

  componentSelectorOpened: boolean = false;
  componentsFilterControl: FormControl<string | null> = new FormControl('');

  selectedComponents: {
    [k: string]: BaseComponent
  } = {};

  filteredComponents$: Observable<Array<BaseComponent & { disabled: boolean }>> = combineLatest([
    this.components$,
    this.componentsInDag$,
  ]).pipe(
    map(([ components, unavailableComponents ]) => {
      const filterResults = [];
      for (const component of components) {
        if (component.display_name.toLowerCase().includes(this.componentsFilterControl.value?.toLowerCase() ?? '')) {
          filterResults.push({
            ...component,
            disabled: unavailableComponents[component.id] ?? false,
          } as BaseComponent & { disabled: boolean });
        }
      }

      return filterResults;
    }),
  );

  journeyId: string;

  constructor(
    private route: ActivatedRoute,
    private store: DagStore,
    private projectStore: ProjectStore,
  ) {
    this.projectStore.current$.pipe(
      takeUntilDestroyed(),
    ).subscribe((project) => {
      this.projectId = project.id;
      this.store.dispatch('getComponents', { parentId: project.id });
    });

    this.componentsFilterControl.valueChanges.pipe(
      debounceTime(300),
      takeUntilDestroyed(),
    ).subscribe((search) => {
      this.store.dispatch('getComponents', { parentId: this.projectId, filters: { search: search || null } });
    });

    this.route.parent!.params.pipe(
      takeUntilDestroyed(),
    ).subscribe(({ id }) => {
      this.journeyId = id;

      this.store.dispatch('getDag', id);
    });

    this.store.loading$.pipe(
      filter(loading => loading.code === 'addEdge' && loading.error),
      takeUntilDestroyed(),
    ).subscribe(({ error }) => {
      this.handleError((error as Error).message);
    });
  }

  addComponent(component: BaseComponent): void {
    this.componentSelectorOpened = false;
    this.store.dispatch('addComponent', this.journeyId, component);
  }

  addEdge(fromNode: string, toNode: string): void {
    this.store.dispatch('addEdge', this.journeyId, fromNode, toNode);
  }

  onNodeSelected({ node, multiple }: { node?: DagNodeDirective, multiple: boolean }): void {
    if (!node) {
      return this.store.dispatch('deselectAll');
    }

    this.store.dispatch('toggleSelection', node.name, multiple, 'Node');
  }

  onEdgeSelected({ edge, multiple }: { edge?: DagEdgeDirective, multiple: boolean }): void {
    if (!edge) {
      return this.store.dispatch('deselectAll');
    }

    this.store.dispatch('toggleSelection', edge.id, multiple, 'Edge');
  }

  @HostListener('window:keydown.backspace', [ '$event' ])
  deleteSelectedOnBackspace(event: KeyboardEvent): void {
    if (event.target === this.dagEl.nativeElement) {
      this.deleteSelected();
    }
  }

  deleteSelected(): void {
    this.store.dispatch('deleteSelected');
  }

  handleError(message: string | undefined): void {
    this.error$.next(message);
  }

  nodeTrackByFn(_: number, node: DagCompleteNode): string {
    return node.info.component.id;
  }

  edgeTrackByFn(_: number, edge: JourneyDagEdge): string {
    return edge.id;
  }

  resetError(): void {
    this.error$.next(undefined);
  }

  onCheckboxChange(component: BaseComponent, checkbox: MatLegacyCheckbox) {
    checkbox.toggle();

    if (!this.selectedComponents[component.id]) {
      this.selectedComponents[component.id] = component;
    } else {
      delete this.selectedComponents[component.id];
    }
  }

  clearSelection() {
    this.selectedComponents = {};
  }

  addComponents() {
    this.componentSelectorOpened = false;
    Object.values(this.selectedComponents).forEach((component) => {
      this.store.dispatch('addComponent', this.journeyId, component);
    });
    this.selectedComponents = {};
  }
}
