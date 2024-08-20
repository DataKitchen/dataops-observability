import { TestBed } from '@angular/core/testing';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { MockProvider } from 'ng-mocks';
import { of, throwError } from 'rxjs';
import { BaseComponent, ComponentType, InstanceDag, JourneyDag, JourneyDagEdge, RunProcessedStatus, TestStatus } from '@observability-ui/core';
import { ComponentsService } from '../../services/components/components.service';
import { JourneysService } from '../../services/journeys/journeys.service';
import { DagStore } from './dag.store';
import { InstancesService } from '../../services/instances/instances.service';

describe('dag.store', () => {
  const projectId = '15';
  const journeyId = '25';
  const components = [
    { id: 'A', name: 'Component A' } as BaseComponent,
    { id: 'B', name: 'Component B' } as BaseComponent,
  ];
  const dag: JourneyDag = {
    nodes: [
      {
        component: components[0],
        edges: [
          { id: 'edge-1', component: undefined },
        ],
      },
      {
        component: components[1],
        edges: [
          { id: 'edge-2', component: undefined },
          { id: 'edge-3', component: 'A' },
        ],
      },
    ],
  };

  const instanceDag: InstanceDag = {
    nodes: [
      {
        component: {
          id: '123',
          type: ComponentType.BatchPipeline,
          key: 'component-a',
          name: 'Component A',
          display_name: 'Component A',
        } as BaseComponent,
        edges: [
          {
            id: '1',
            component: null,
          }
        ],
        status: RunProcessedStatus.Completed,
        alerts_summary: [],
        operations_summary: [],
        runs_summary: [],
        tests_summary: [
          {status: TestStatus.Passed, count: 2},
          {status: TestStatus.Warning, count: 1},
        ],
      },
      {
        component: {
          id: '1234',
          type: ComponentType.BatchPipeline,
          key: 'component-a',
          name: 'Component A',
          display_name: 'Component A',
        } as BaseComponent,
        edges: [
          {
            id: '2',
            component: '123',
          }
        ],
        status: RunProcessedStatus.Completed,
        alerts_summary: [
          {level: 'ERROR', description: '...', count: 2},
        ],
        operations_summary: [
          {operation: 'WRITE', count: 1},
          {operation: 'READ', count: 1},
        ],
        runs_summary: [
          {status: RunProcessedStatus.Missing, count: 1}
        ],
        tests_summary: [],
      },
    ],
  };

  let store: DagStore;
  let journeysService: JourneysService;
  let componentsService: ComponentsService;
  let instanceService: InstancesService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        DagStore,
        MockProvider(JourneysService, {
          getJourneyDag: jest.fn().mockReturnValue(of(dag)),
          createJourneyDagEdge: jest.fn().mockReturnValue(of({})),
          deleteJourneyDagEdge: jest.fn().mockReturnValue(of({})),
        }),
        MockProvider(ComponentsService, {
          findAll: jest.fn().mockReturnValue(of(components)),
          getPage: jest.fn().mockReturnValue(of(components)),
          getSchedules: jest.fn().mockReturnValue(of([]))
        }),
        MockProvider(InstancesService, {
          getDag: jest.fn().mockReturnValue(of(instanceDag)),
        }),
      ],
    });

    store = TestBed.inject(DagStore);
    journeysService = TestBed.inject(JourneysService);
    componentsService = TestBed.inject(ComponentsService);
    instanceService = TestBed.inject(InstancesService);
  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

  describe('canDelete$', () => {
    it('should not allow deleting if nothing is selected', () => {
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.canDelete$).toBe('a', { a: false });
      });
    });

    it('should allow deleting if at least one node selected', () => {
      store.dispatch('toggleSelection', 'A', false, 'Node');
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.canDelete$).toBe('a', { a: true });
      });
    });

    it('should allow deleting if at least one edge selected', () => {
      store.dispatch('toggleSelection', 'edge-3', false, 'Edge');
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.canDelete$).toBe('a', { a: true });
      });
    });
  });

  describe('getComponents', () => {
    it('should get all components from the service', () => {
      store.getComponents({ parentId: projectId });
      expect(componentsService.getPage).toBeCalledWith({ parentId: projectId, count: 50, page: 0 });
    });

    it('should update the store with the list of components', () => {
      expect(store.onGetComponents({} as any, components)).toEqual(expect.objectContaining({ components }));
    });
  });

  describe('getDag', () => {
    it('should get the dag from the service', () => {
      store.getDag(journeyId);
      expect(journeysService.getJourneyDag).toBeCalledWith(journeyId);
    });

    it('should include all the nodes from the dag in the store', () => {
      expect(store.onGetDag({} as any, dag)).toEqual(expect.objectContaining({
        nodes: [ expect.objectContaining(dag.nodes[0]), expect.objectContaining(dag.nodes[1]) ],
      }));
    });

    it('should include all the edges from the dag in the store', () => {
      expect(store.onGetDag({} as any, dag)).toEqual(expect.objectContaining({
        edges: [
          { id: 'edge-1', from: undefined, to: 'A' },
          { id: 'edge-2', from: undefined, to: 'B' },
          { id: 'edge-3', from: 'A', to: 'B' },
        ],
      }));
    });

    it('should mark the components as used', () => {
      expect(store.onGetDag({} as any, dag)).toEqual(expect.objectContaining({
        componentsInDag: { A: true, B: true },
      }));
    });
  });

  describe('toggleSelection', () => {
    it('should emit the selection id, type and the multiple flag ', () => {
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.toggleSelection('A', true, 'Edge')).toBe('(a|)', {
          a: {
            id: 'A',
            multiple: true,
            type: 'Edge'
          }
        });
      });
    });

    it('should set a node selected', () => {
      expect(store.onToggleSelection({} as any, {
        id: 'node-a',
        multiple: false,
        type: 'Node'
      })).toEqual(expect.objectContaining({
        selectedNodes: { 'node-a': true },
      }));
    });

    it('should set an edge selected', () => {
      expect(store.onToggleSelection({} as any, {
        id: 'edge-1',
        multiple: false,
        type: 'Edge'
      })).toEqual(expect.objectContaining({
        selectedEdges: { 'edge-1': true },
      }));
    });

    it('should set multiple nodes and edges as selected', () => {
      let state = {} as any;
      state = store.onToggleSelection(state, { id: 'edge-1', multiple: false, type: 'Edge' });

      expect(store.onToggleSelection(state, {
        id: 'node-a',
        multiple: true,
        type: 'Node'
      })).toEqual(expect.objectContaining({
        selectedNodes: { 'node-a': true },
        selectedEdges: { 'edge-1': true },
      }));
    });

    it('should deselect all previous selection if multiple flag is not set', () => {
      let state = {} as any;
      state = store.onToggleSelection(state, { id: 'node-a', multiple: false, type: 'Node' });
      state = store.onToggleSelection(state, { id: 'node-b', multiple: true, type: 'Node' });
      state = store.onToggleSelection(state, { id: 'edge-1', multiple: true, type: 'Edge' });

      expect(store.onToggleSelection(state, {
        id: 'node-c',
        multiple: false,
        type: 'Node'
      })).toEqual(expect.objectContaining({
        selectedEdges: {},
        selectedNodes: { 'node-c': true },
      }));
    });
  });

  describe('deselectAll', () => {
    it('should reset all selections', () => {
      expect(store.onDeselectAll({} as any)).toEqual(expect.objectContaining({ selectedNodes: {}, selectedEdges: {} }));
    });
  });

  describe('addEdge', () => {
    it('should create the new edge using the service', () => {
      store.dispatch('addComponent', journeyId, components[0]);
      store.dispatch('addComponent', journeyId, components[1]);

      new TestScheduler().run(({ flush }) => {
        store.addEdge(journeyId, components[0].id, components[1].id).subscribe();
        flush();
        expect(journeysService.createJourneyDagEdge).toBeCalledWith(journeyId, components[0].id, components[1].id);
      });
    });

    it('should push the new edge to the store', () => {
      const edge = { id: 'A', from: 'node-a', to: 'node-b' };
      expect(store.onAddEdge({ edges: [] } as any, edge)).toEqual(expect.objectContaining({
        edges: [ edge ],
      }));
    });

    it('should error out if that edge already exists', () => {
      store.dispatch('addComponent', journeyId, components[0]);
      store.dispatch('addComponent', journeyId, components[1]);
      store.dispatch('addEdge', journeyId, components[0].id, components[1].id);

      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.addEdge(journeyId, components[0].id, components[1].id)).toEqual(throwError(() => new Error('Cannot duplicate dependency. A relationship already exists here.')));
      });
    });

    it('should error out if that edge will cause a cycle', () => {
      store.dispatch('addComponent', journeyId, components[0]);
      store.dispatch('addComponent', journeyId, components[1]);
      store.dispatch('addEdge', journeyId, components[0].id, components[1].id);

      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.addEdge(journeyId, components[1].id, components[0].id)).toEqual(throwError(() => new Error('Cannot add dependency. This relationship creates a loop.')));
      });
    });
  });

  describe('addComponent', () => {
    it('should add the new component node using the service', () => {
      store.addComponent(journeyId, { id: 'component-a' } as BaseComponent);
      expect(journeysService.createJourneyDagEdge).toBeCalledWith(journeyId, undefined, 'component-a');
    });

    it('should push the new component to the store as a node', () => {
      const component = { id: 'component-a' } as BaseComponent;
      const edge = { id: 'edge-1', from: undefined, to: '' } as JourneyDagEdge;
      expect(store.onAddComponent({ nodes: [], edges: [], componentsInDag: {} } as any, {
        component,
        edge
      })).toEqual(
        expect.objectContaining({
          nodes: [{ component, edges: [] }],
        })
      );
    });

    it('should push the new edge to the store', () => {
      const component = { id: 'component-a' } as BaseComponent;
      const edge = { id: 'edge-1', from: undefined, to: '' } as JourneyDagEdge;
      expect(store.onAddComponent({ nodes: [], edges: [], componentsInDag: {} } as any, {
        component,
        edge
      })).toEqual(expect.objectContaining({
        edges: [ edge ],
      }));
    });

    it('should mark the new component as used', () => {
      const component = { id: 'component-a' } as BaseComponent;
      const edge = { id: 'edge-1', from: undefined, to: '' } as JourneyDagEdge;
      expect(store.onAddComponent({ nodes: [], edges: [], componentsInDag: {} } as any, {
        component,
        edge
      })).toEqual(expect.objectContaining({
        componentsInDag: { 'component-a': true },
      }));
    });
  });

  describe('updateNodeInfo', () => {
    it('should update a node\'s component if it is in the DAG', () => {
      const component = { id: 'component-a', display_name: 'original' } as BaseComponent;
      expect(store.onUpdateNodeInfo({ nodes: [ { component , edges: [] } ] } as any, {
        ...component,
        display_name: 'new'
      })).toEqual(expect.objectContaining({
        nodes: [ {
          component: {...component, display_name: 'new' },
          edges: []
        } ]
      }));
    });

    it('should not add a component to the DAG', () => {
      const component = { id: 'component-a', display_name: 'original' } as BaseComponent;
      expect(store.onUpdateNodeInfo({ nodes: [] } as any, {
        ...component,
        display_name: 'new'
      })).toEqual(expect.objectContaining({ nodes: [] }));
    });
  });

  describe('deleteSelected', () => {
    beforeEach(() => {
      store.dispatch('getDag', journeyId);
    });

    it('should exclude selected nodes from the dag', () => {
      store.dispatch('toggleSelection', components[1].id, true, 'Node');

      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.deleteSelected()).toBe('(a|)', {
          a: expect.objectContaining({
            nodes: [
              dag.nodes[0],
            ],
          }),
        });
      });
    });

    it('should unmark deleted nodes to make them available again', () => {
      store.dispatch('toggleSelection', 'B', true, 'Node');

      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.deleteSelected()).toBe('(a|)', {
          a: expect.objectContaining({
            componentsInDag: { [components[0].id]: true },
          }),
        });
      });
    });

    it('should exclude deleted edges from the dag', () => {
      store.dispatch('toggleSelection', 'edge-3', true, 'Edge');

      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.deleteSelected()).toBe('(a|)', {
          a: expect.objectContaining({
            edges: [ { id: 'edge-1', from: undefined, to: 'A' }, { id: 'edge-2', from: undefined, to: 'B' } ],
          }),
        });
      });
    });

    it('should delete all selected edges using the service', () => {
      store.dispatch('toggleSelection', 'edge-3', true, 'Edge');
      store.deleteSelected().subscribe();

      expect(journeysService.deleteJourneyDagEdge).toBeCalledWith('edge-3');
    });

    it('should delete all single-node for all deleted nodes using the service', () => {
      store.dispatch('toggleSelection', 'A', true, 'Node');
      store.dispatch('toggleSelection', 'B', true, 'Node');
      store.deleteSelected().subscribe();

      expect(journeysService.deleteJourneyDagEdge).toBeCalledWith('edge-1');
      expect(journeysService.deleteJourneyDagEdge).toBeCalledWith('edge-2');
      expect(journeysService.deleteJourneyDagEdge).toBeCalledWith('edge-3');
    });

    it('should reset selected nodes', () => {
      store.dispatch('toggleSelection', 'A', true, 'Node');

      expect(store.onDeleteSelected({} as any, {
        edges: [],
        nodes: [],
        componentsInDag: {}
      })).toEqual(expect.objectContaining({
        selectedNodes: {},
      }));
    });

    it('should reset selected edges', () => {
      store.dispatch('toggleSelection', 'edge-3', true, 'Edge');

      expect(store.onDeleteSelected({} as any, {
        edges: [],
        nodes: [],
        componentsInDag: {}
      })).toEqual(expect.objectContaining({
        selectedEdges: {},
      }));
    });
  });

  describe('getInstanceDag', () => {
    const instanceId = '15';

    beforeEach(() => {
      store.dispatch('getInstanceDag', instanceId);
    });

    it('should get the dag from the instance service', () => {
      expect(instanceService.getDag).toBeCalledWith(instanceId);
    });

    it('should update the store with the list of nodes', () => {
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.nodes$).toBe('a', {
          a: instanceDag.nodes.map((n) => ({ ...n, selected: false })),
        });
      });
    });

    it('should update the store with the list of edges', () => {
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.edges$).toBe('a', {
          a: instanceDag.nodes
            .reduce(
              (edges, n) => [
                ...edges,
                ...n.edges.map((edge) => ({id: edge.id, from: edge.component, to: n.component.id, selected: false})),
              ],
              [] as JourneyDagEdge[]
            )
            .filter((edge) => !!edge.from),
        });
      });
    });

    it('should set components in DAG', () => {
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.componentsInDag$).toBe('a', {
          a: instanceDag.nodes.reduce((result, n) => ({ ...result, [n.component.id]: true }), {}),
        });
      });
    });
  });
});
