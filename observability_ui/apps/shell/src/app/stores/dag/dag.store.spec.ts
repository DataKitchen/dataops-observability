import { TestBed } from '@angular/core/testing';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { MockProvider } from 'ng-mocks';
import { of, throwError } from 'rxjs';
import { BaseComponent, ComponentType, EventTypes, InstanceAlert, InstanceAlertType, JourneyDag, JourneyDagEdge, JourneyDagNode, ProjectService } from '@observability-ui/core';
import { ComponentsService } from '../../services/components/components.service';
import { JourneysService } from '../../services/journeys/journeys.service';
import { DagStore } from './dag.store';
import { ProjectRunsService } from '../../services/project-runs/project-runs.service';

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

  const runs = [
    {
      'end_time': '2023-02-18T03:52:23',
      'id': 'f05db1f5-3430-4067-a06d-75cbbeafcc65',
      'key': 'def',
      'listening': false,
      'pipeline': { 'display_name': 'aarthy_g', 'id': '362154b4-5653-49dd-8d73-601264da30b7', 'key': 'aarthy_g' },
      'run_states': [],
      'start_time': '2023-02-18T03:52:17',
      'status': 'COMPLETED',
      'tasks_summary': [ { 'count': 0, 'status': 'MISSING' }, {
        'count': 0,
        'status': 'COMPLETED_WITH_WARNINGS'
      }, { 'count': 0, 'status': 'RUNNING' }, { 'count': 0, 'status': 'PENDING' }, {
        'count': 0,
        'status': 'COMPLETED'
      }, { 'count': 0, 'status': 'FAILED' } ]
    },
    {
      'end_time': '2023-02-18T03:09:44',
      'id': '6baf5e8d-fd57-4f76-958e-c718bae30eb4',
      'key': 'abc',
      'listening': false,
      'pipeline': {
        'display_name': 'Aarthy Pipeline E',
        'id': 'a577e35a-d0ae-44b9-b952-1be76a94b849',
        'key': 'aarthy_e'
      },
      'run_states': [] as any[],
      'start_time': '2023-02-18T02:20:24',
      'status': 'COMPLETED',
      'tasks_summary': [ { 'status': 'RUNNING' }, { 'count': 0, 'status': 'MISSING' }, {
        'count': 0,
        'status': 'FAILED'
      }, { 'count': 0, 'status': 'COMPLETED_WITH_WARNINGS' }, { 'count': 0, 'status': 'COMPLETED' }, {
        'count': 0,
        'status': 'PENDING'
      } ]
    },
    {
      'end_time': '2023-02-18T03:10:03',
      'id': 'fcf7de49-1208-4492-921d-fcfa612731f2',
      'key': 'abc',
      'listening': false,
      'pipeline': { 'display_name': 'aarthy_f', 'id': '347f5dda-d620-40f3-ac4e-e6f73ddea4f3', 'key': 'aarthy_f' },
      'run_states': [],
      'start_time': '2023-02-18T03:09:58',
      'status': 'COMPLETED',
      'tasks_summary': [ { 'count': 0, 'status': 'MISSING' }, {
        'count': 0,
        'status': 'COMPLETED_WITH_WARNINGS'
      }, { 'count': 0, 'status': 'RUNNING' }, { 'count': 0, 'status': 'PENDING' }, {
        'count': 0,
        'status': 'COMPLETED'
      }, { 'count': 0, 'status': 'FAILED' } ]
    }
  ];

  const tests = [ { id: 'test-id-1', name: 'test 1' }, { id: 'test-id-2', name: 'test 2' } ];

  const alerts = [
    {
      id: '1',
      run: null,
      level: 'ERROR',
      type: InstanceAlertType.OutOfSequence,
      name: 'Some Alert',
      description: '',
      created_on: null,
      components: [],
    } as InstanceAlert,
  ];

  let store: DagStore;
  let journeysService: JourneysService;
  let componentsService: ComponentsService;
  let runService: ProjectRunsService;
  let projectService: ProjectService;

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
        MockProvider(ProjectRunsService, {
          findAll: jest.fn().mockReturnValue(of({ entities: runs, total: runs.length })),
        }),
        MockProvider(ProjectService, {
          getTestById: jest.fn().mockReturnValue(of(tests[1])),
          getTests: jest.fn().mockReturnValue(of({ entities: tests, total: tests.length })),
          getAllTests: jest.fn().mockReturnValue(of({ entities: [] })),
          getAllEvents: jest.fn().mockReturnValue(of({ entities: [] })),
          getAlerts: jest.fn().mockReturnValue(of({ entities: alerts, total: alerts.length })),
        }),
      ],
    });

    store = TestBed.inject(DagStore);
    journeysService = TestBed.inject(JourneysService);
    componentsService = TestBed.inject(ComponentsService);
    runService = TestBed.inject(ProjectRunsService);
    projectService = TestBed.inject(ProjectService);
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
        nodes: [ expect.objectContaining({ info: dag.nodes[0] }), expect.objectContaining({ info: dag.nodes[1] }) ],
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
          nodes: [{ info: { component, edges: [] }}],
        })
        // {}
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
      expect(store.onUpdateNodeInfo({ nodes: [ { info: { component } , edges: [] } ] } as any, {
        ...component,
        display_name: 'new'
      })).toEqual(expect.objectContaining({
        nodes: [ {
          info: { component: {...component, display_name: 'new' }},
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
      store.dispatch('toggleSelection', 'B', true, 'Node');

      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(store.deleteSelected()).toBe('(a|)', {
          a: expect.objectContaining({
            nodes: [ {
              info: {
                component: { id: 'A', name: 'Component A' },
                edges: expect.anything()
              }
            } ],


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

  describe('getDagNodeDetail', () => {
    const instanceId = '15';
    const projectId = '1';


    it('should get all the runs from the service if component is batch pipeline', () => {
      const node: JourneyDagNode = {
        component: {
          id: '2',
          type: ComponentType.BatchPipeline
        }
      } as any;

      store.dispatch('getDagNodeDetail', projectId, instanceId, node);

      expect(runService.findAll).toBeCalledWith({
        parentId: projectId,
        filters: { instance_id: instanceId, pipeline_id: node.component.id }
      });
    });

    it('should get all the events from the service if component is dataset', () => {
      const node: JourneyDagNode = {
        component: {
          id: '2',
          type: ComponentType.Dataset
        }
      } as any;

      store.dispatch('getDagNodeDetail', projectId, instanceId, node);

      expect(projectService.getAllEvents).toBeCalledWith({
        parentId: projectId,
        filters: {
          instance_id: instanceId,
          component_id: node.component.id,
          event_type: EventTypes.DatasetOperationEvent.toString()
        }
      });
    });

    it('should get all the schedules from the service if component is dataset', () => {
      const node: JourneyDagNode = {
        component: {
          id: '2',
          type: ComponentType.Dataset
        }
      } as any;

      store.dispatch('getDagNodeDetail', projectId, instanceId, node);

      expect(componentsService.getSchedules).toBeCalledWith(node.component.id);
    });
  });
});
