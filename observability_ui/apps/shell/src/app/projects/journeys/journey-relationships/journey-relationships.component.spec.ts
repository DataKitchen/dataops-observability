import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { OverlayModule } from '@angular/cdk/overlay';
import { BaseComponent, JourneyDagEdge, ProjectStore } from '@observability-ui/core';
import { LoadingState } from '@microphi/store';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { MockComponent, MockModule, MockProvider } from 'ng-mocks';
import { BehaviorSubject, of } from 'rxjs';
import { JourneyRelationshipsComponent } from './journey-relationships.component';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MatIcon } from '@angular/material/icon';
import { DagComponent, DagEdgeDirective, DagNodeDirective, DkTooltipModule } from '@observability-ui/ui';
import { Mocked } from '@datakitchen/ngx-toolkit';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { RouterTestingModule } from '@angular/router/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { DagCompleteNode, DagStore } from '../../../stores/dag/dag.store';
import { JourneyDagLegendComponent } from '../../journey-dag-legend/journey-dag-legend.component';

describe('Journey Relationships', () => {
  const project = { id: '15' };
  const journey = { id: '2' };
  const allComponents = [
    { id: '1', display_name: 'Component A' },
    { id: '2', display_name: 'Component B' },
    { id: '3', display_name: 'Component C' },
    { id: '4', display_name: 'Component D' },
    { id: '5', display_name: 'Component E' },
  ];
  const nodes = [
    { component: allComponents[0], edges: [] as any },
    { component: allComponents[1], edges: [] },
    { component: allComponents[2], edges: [] },
  ];
  const edges = [
    { id: 'edge-1', from: '1', to: undefined },
    { id: 'edge-3', from: '2', to: undefined },
    { id: 'edge-2', from: '3', to: undefined },
    { id: 'edge-4', from: '1', to: '3' },
  ];

  let component: JourneyRelationshipsComponent;
  let fixture: ComponentFixture<JourneyRelationshipsComponent>;

  let router: Router;
  let loadingValue$: BehaviorSubject<boolean>;
  let loadingAction$: BehaviorSubject<LoadingState<DagStore>>;
  let selectedNodes$: BehaviorSubject<{ [componentId: string]: boolean }>;
  let selectedEdges$: BehaviorSubject<{ [edgeId: string]: boolean }>;
  let componentsInDag$: BehaviorSubject<{ [componentId: string]: boolean }>;

  let store: Mocked<DagStore>;

  beforeEach(async () => {
    loadingValue$ = new BehaviorSubject(false);
    loadingAction$ = new BehaviorSubject({} as LoadingState<DagStore>);
    selectedNodes$ = new BehaviorSubject({});
    selectedEdges$ = new BehaviorSubject({});
    componentsInDag$ = new BehaviorSubject({});

    TestBed.configureTestingModule({
      declarations: [
        JourneyRelationshipsComponent,
        TranslatePipeMock,
        MockComponent(MatIcon),
        MockComponent(DagComponent),
        MockComponent(JourneyDagLegendComponent),
      ],
      imports: [
        RouterTestingModule,
        ReactiveFormsModule,
        MockModule(OverlayModule),
        MockModule(DkTooltipModule),
      ],
      providers: [
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock(
            {},
            {},
            ActivatedRouteMock(
              { id: journey.id },
              {},
              ActivatedRouteMock(
                {},
                {},
                ActivatedRouteMock({}, {})
              )
            )
          ),
        },
        MockProvider(ProjectStore, {
          current$: of(project),
        } as any),
      ],
    }).overrideProvider(DagStore, {
      useFactory: () => {
        return new class {
          nodes$ = of([]);
          edges$ = of([]);
          components$ = of(allComponents);
          selectedNodes$ = selectedNodes$;
          selectedEdges$ = selectedEdges$;
          componentsInDag$ = componentsInDag$;
          canDelete$ = of(false);
          loading$ = loadingAction$;
          dispatch = jest.fn();
          getLoadingFor = jest.fn().mockReturnValue(loadingValue$);
        };
      }

    });

    router = TestBed.inject(Router);
    store = TestBed.inject(DagStore) as Mocked<DagStore>;

    fixture = TestBed.createComponent(JourneyRelationshipsComponent);
    component = fixture.componentInstance;

    jest.spyOn(router, 'navigate').mockImplementation();

    fixture.detectChanges();

    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  xit('should get the list of components from the store', () => {
    expect(store.dispatch).toBeCalledWith('getComponents', { parentId: project.id });
  });

  it('should disable existing nodes from being added more than once', () => {
    const nodeIds = nodes.map(n => n.component.id);
    const disabledComponents = allComponents.map(c => ({ ...c, disabled: nodeIds.includes(c.id) }));

    new TestScheduler().run(({ expectObservable }) => {
      componentsInDag$.next(nodes.reduce((acc, n) => ({ ...acc, [n.component.id]: true }), {}));
      expectObservable(component.filteredComponents$).toBe('a', { a: disabledComponents });
    });
  });

  xit('should get the DAG from the store', () => {
    expect(store.dispatch).toBeCalledWith('getDag', journey.id);
  });

  it('should next the error observable if an error happens', () => {
    const error = new Error('something bad happened');
    new TestScheduler().run(({ flush }) => {
      loadingAction$.next({ code: 'addEdge', status: false, error });
      flush();
      expect(component.error$.getValue()).toEqual(error.message);
    });
  });

  describe('addComponents()', () => {
    it('should close the component selector', () => {
      component.addComponents();
      expect(component.componentSelectorOpened).toBeFalsy();
    });

    xit('should add the new components as nodes', () => {
      component.selectedComponents = { [allComponents[3].id]: allComponents[3] as BaseComponent };

      component.addComponents();
      expect(store.dispatch).toHaveBeenLastCalledWith('addComponent', journey.id, allComponents[3]);
    });
  });

  describe('clearSelection', () => {
    it('should reset the selected components array', () => {
      component.clearSelection();
      expect(component.selectedComponents).toEqual({});
    });
  });

  describe('onCheckboxChange', () => {
    const checkbox = { checked: false, toggle: jest.fn() };

    it('should toggle the checkbox', () => {
      component.onCheckboxChange({ id: '1' } as BaseComponent, checkbox as any);

      expect(checkbox.toggle).toBeCalled();
    });

    it('should push to selectedComponents if the component is not selected', () => {
      component.onCheckboxChange({ id: '1' } as BaseComponent, checkbox as any);

      expect(component.selectedComponents).toEqual({ '1': { id: '1' } });
    });

    it('should remove from selectedComponents if the component is already selected', () => {
      component.selectedComponents = { '1': { id: '1' } as BaseComponent };
      component.onCheckboxChange({ id: '1' } as BaseComponent, checkbox as any);

      expect(component.selectedComponents).toEqual({});
    });
  });

  describe('addEdge()', () => {
    xit('should add an edge between the two nodes', () => {
      const from = nodes[2].component.id;
      const to = nodes[1].component.id;
      component.addEdge(from, to);
      expect(store.dispatch).toBeCalledWith('addEdge', journey.id, from, to);
    });
  });

  describe('onNodeSelected()', () => {
    xit('should deselect everything if no node is provided', () => {
      component.onNodeSelected({ multiple: false });
      expect(store.dispatch).toBeCalledWith('deselectAll');
    });

    xit('should toggle items selection', () => {
      component.onNodeSelected({ node: { name: nodes[0].component.id } as DagNodeDirective, multiple: false });
      expect(store.dispatch).toBeCalledWith('toggleSelection', nodes[0].component.id, false, 'Node');
    });

    xit('should toggle selection for multiple items', () => {
      component.onNodeSelected({ node: { name: nodes[0].component.id } as DagNodeDirective, multiple: true });
      expect(store.dispatch).toBeCalledWith('toggleSelection', nodes[0].component.id, true, 'Node');
    });
  });

  describe('onEdgeSelected()', () => {
    xit('should deselect everything if no edge is provided', () => {
      component.onEdgeSelected({ multiple: false });
      expect(store.dispatch).toBeCalledWith('deselectAll');
    });

    xit('should toggle items selection', () => {
      component.onEdgeSelected({ edge: { id: 'edge-1' } as DagEdgeDirective, multiple: false });
      expect(store.dispatch).toBeCalledWith('toggleSelection', 'edge-1', false, 'Edge');
    });

    xit('should toggle selection for multiple items', () => {
      component.onEdgeSelected({ edge: { id: 'edge-2' } as DagEdgeDirective, multiple: true });
      expect(store.dispatch).toBeCalledWith('toggleSelection', 'edge-2', true, 'Edge');
    });
  });

  xdescribe('deleteSelected()', () => {
    it('should deleted selected items', () => {
      component.deleteSelected();
      expect(store.dispatch).toBeCalledWith('deleteSelected');
    });
  });

  describe('handleError()', () => {
    it('should next the error subject', () => {
      component.handleError('something just happened');
      expect(component.error$.getValue()).toEqual('something just happened');
    });
  });

  describe('nodeTrackByFn()', () => {
    it('should track nodes by component id', () => {
      expect(component.nodeTrackByFn(0, { info: nodes[0] } as unknown as DagCompleteNode)).toEqual(nodes[0].component.id);
    });
  });

  describe('edgeTrackByFn()', () => {
    it('should track edges by id', () => {
      expect(component.edgeTrackByFn(0, edges[0] as JourneyDagEdge)).toEqual(edges[0].id);
    });
  });

  describe('resetError()', () => {
    it('should empty the error subject', () => {
      component.resetError();
      expect(component.error$.getValue()).toBeUndefined();
    });
  });
});
