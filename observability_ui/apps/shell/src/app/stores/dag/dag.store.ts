import { Injectable } from '@angular/core';
import { Effect, makeStore, Reduce, Store } from '@microphi/store';
import { defer, forkJoin, iif, map, Observable, of, throwError } from 'rxjs';
import { BaseComponent, ComponentType, EntityListResponse, EventType, EventTypes, getDatasetStatus, getSummary, InstanceDagNode, InstanceRunSummary, InstanceTestSummary, mostImportantStatus, PaginatedRequest, ProjectService, Run, Schedule, TestOutcomeItem } from '@observability-ui/core';
import { JourneyDag, JourneyDagEdge, JourneyDagNode } from '@observability-ui/core';
import { ComponentsService } from '../../services/components/components.service';
import { JourneysService } from '../../services/journeys/journeys.service';
import { ProjectRunsService } from '../../services/project-runs/project-runs.service';

export interface DagCompleteNode {
  info: JourneyDagNode;
  details?: InstanceDagNode;
}

interface DagState {
  journeyId?: string;
  components: BaseComponent[];

  nodes: DagCompleteNode[];
  edges: JourneyDagEdge[];

  componentsInDag: { [componentId: string]: boolean };

  selectedEdges: { [edgeId: string]: boolean };
  selectedNodes: { [nodeId: string]: boolean };
}

interface DagActions {
  getDag(id: string): Observable<JourneyDag>;

  getComponents(req: PaginatedRequest): Observable<BaseComponent[]>;

  toggleSelection(id: string, multiple: boolean, type: 'Node' | 'Edge'): Observable<{
    id: string,
    multiple: boolean,
    type: 'Node' | 'Edge'
  }>;

  deselectAll(): Observable<undefined>;

  addEdge(journeyId: string, fromNode: string, toNode: string): Observable<JourneyDagEdge>;

  addComponent(journeyId: string, component: BaseComponent): Observable<{
    component: BaseComponent,
    edge: JourneyDagEdge
  }>;

  updateNodeInfo(component: BaseComponent): Observable<BaseComponent>;

  deleteSelected(): Observable<{
    edges: JourneyDagEdge[];
    nodes: DagCompleteNode[],
    componentsInDag: { [componentId: string]: boolean }
  }>;

  getDagNodeDetail(projectId: string, instanceId: string, node: JourneyDagNode): Observable<[ EntityListResponse<TestOutcomeItem>, EntityListResponse<Run>, JourneyDagNode, EntityListResponse<EventType>, EntityListResponse<Schedule> ]>;
}


@Injectable({
  providedIn: 'root',
})
export class DagStore extends Store<DagState, DagActions> implements makeStore<DagState, DagActions> {
  nodes$: Observable<Array<DagCompleteNode & { selected?: boolean }>> = this.select(state => {
    const nodes = [];
    for (const node of state.nodes) {
      nodes.push({ ...node, selected: state.selectedNodes[node.info.component.id] ?? false });
    }
    return nodes;
  });
  edges$: Observable<Array<JourneyDagEdge & { selected?: boolean }>> = this.select(state => {
    const edges = [];
    for (const edge of state.edges) {
      if (edge.from) {
        edges.push({ ...edge, selected: state.selectedEdges[edge.id] ?? false });
      }
    }
    return edges;
  });
  components$ = this.select(state => state.components);
  componentsInDag$ = this.select(state => state.componentsInDag);

  canDelete$ = this.select(state => (Object.keys(state.selectedEdges).length + Object.keys(state.selectedNodes).length) > 0);

  constructor(
    private journeyService: JourneysService,
    private componentsService: ComponentsService,
    private projectService: ProjectService,
    private runsService: ProjectRunsService
  ) {
    super({
      components: [],
      nodes: [],
      edges: [],
      componentsInDag: {},
      selectedEdges: {},
      selectedNodes: {},
    });
  }

  @Effect()
  getDag(id: string): Observable<JourneyDag> {
    return this.journeyService.getJourneyDag(id);
  }

  @Reduce()
  onGetDag(state: DagState, dag: JourneyDag): DagState {
    const nodes: DagCompleteNode[] = [];
    const edges: Array<JourneyDagEdge> = [];
    const componentsInDag: { [componentId: string]: boolean } = {};

    for (const node of dag.nodes) {
      nodes.push({ info: node });
      for (const { id, component } of node.edges) {
        edges.push({ id, from: component, to: node.component.id });
      }
      componentsInDag[node.component.id] = true;
    }

    return {
      ...state,
      nodes,
      edges,
      componentsInDag,
    };
  }

  @Effect()
  getComponents(req: PaginatedRequest): Observable<BaseComponent[]> {
    // TODO: Use 'getPage' with a limited number instead and filter on the server side -- Rendering less items and forcing users to be specific on their search
    return this.componentsService.getPage({ ...req, count: 50, page: 0 }).pipe(
      map(({ entities }) => entities),
    );
  }

  @Reduce()
  onGetComponents(state: DagState, components: BaseComponent[]): DagState {
    return { ...state, components };
  }

  @Effect()
  toggleSelection(id: string, multiple: boolean, type: 'Node' | 'Edge'): Observable<{
    id: string,
    multiple: boolean,
    type: 'Node' | 'Edge'
  }> {
    return of({ id, multiple, type });
  }

  @Reduce()
  onToggleSelection(state: DagState, payload: { id: string, multiple: boolean, type: 'Node' | 'Edge' }): DagState {
    let selectedNodes = state.selectedNodes;
    let selectedEdges = state.selectedEdges;

    if (!payload.multiple) {
      selectedNodes = {};
      selectedEdges = {};
    }

    const selectionByType = { 'Node': selectedNodes, 'Edge': selectedEdges };
    const selection = selectionByType[payload.type];
    if (selection[payload.id]) {
      delete selection[payload.id];
    } else {
      selection[payload.id] = true;
    }

    return { ...state, selectedEdges, selectedNodes };
  }

  @Effect()
  deselectAll(): Observable<undefined> {
    return of(undefined);
  }

  @Reduce()
  onDeselectAll(state: DagState): DagState {
    return { ...state, selectedNodes: {}, selectedEdges: {} };
  }

  @Effect('concatMap')
  addEdge(journeyId: string, fromNode: string, toNode: string): Observable<JourneyDagEdge> {
    const state = this._store$.getValue();

    const noEdgeBetweenTheSelectedNodes = !state.edges.some(edge => edge.from === fromNode && edge.to === toNode);
    const willNotCauseCycles = !this.hasCycles(state.nodes.map(n => n.info), [ ...state.edges, {
      id: 'Any',
      from: fromNode,
      to: toNode
    } ]);

    let errorMessage = '';
    if (!noEdgeBetweenTheSelectedNodes) {
      errorMessage = 'Cannot duplicate dependency. A relationship already exists here.';
    } else if (!willNotCauseCycles) {
      errorMessage = 'Cannot add dependency. This relationship creates a loop.';
    }

    return iif(
      () => (noEdgeBetweenTheSelectedNodes && willNotCauseCycles),
      defer(() => this.journeyService.createJourneyDagEdge(journeyId, fromNode, toNode).pipe(
        map(edge => ({ id: edge.id, from: fromNode, to: toNode } as JourneyDagEdge))
      )),
      throwError(() => new Error(errorMessage)),
    );
  }

  @Reduce()
  onAddEdge(state: DagState, edge: JourneyDagEdge): DagState {
    return { ...state, edges: [ ...state.edges, edge ] };
  }

  @Effect('concatMap')
  addComponent(journeyId: string, component: BaseComponent): Observable<{
    component: BaseComponent,
    edge: JourneyDagEdge
  }> {
    return this.journeyService.createJourneyDagEdge(journeyId, undefined, component.id).pipe(
      map((edge) => ({ component, edge: { id: edge.id, from: edge.left, to: edge.right } as JourneyDagEdge })),
    );
  }

  @Reduce()
  onAddComponent(state: DagState, { component, edge }: { component: BaseComponent, edge: JourneyDagEdge }): DagState {
    const componentsInDag = state.componentsInDag;
    componentsInDag[component.id] = true;

    return {
      ...state,
      componentsInDag,
      nodes: [ ...state.nodes, { info: { component: component, edges: [] } } ],
      edges: [ ...state.edges, edge ],
    };
  }

  @Effect()
  updateNodeInfo(component: BaseComponent): Observable<BaseComponent> {
    return of(component);
  }

  @Reduce()
  onUpdateNodeInfo(state: DagState, component: BaseComponent): DagState {
    const nodes = state.nodes;
    const nodeIdx = nodes.findIndex(n => n.info.component.id === component.id);
    if (nodeIdx > -1) {
      nodes[nodeIdx] = { ...nodes[nodeIdx], info: { ...nodes[nodeIdx].info, component: component } };
      return { ...state, nodes };
    }

    return state;
  }

  @Effect('concatMap')
  deleteSelected(): Observable<{
    edges: JourneyDagEdge[];
    nodes: DagCompleteNode[],
    componentsInDag: { [componentId: string]: boolean }
  }> {
    const state = this._store$.getValue();
    const edgesToDelete: Set<string> = new Set();
    const componentsInDag = { ...state.componentsInDag };
    let edges = state.edges;
    let nodes = state.nodes;

    for (const [ nodeId, ] of Object.entries(state.selectedNodes)) {
      nodes = nodes.filter(node => node.info.component.id !== nodeId);
      delete componentsInDag[nodeId];
    }

    for (const edge of edges) {
      if (state.selectedNodes[edge.from ?? ''] || state.selectedNodes[edge.to] || state.selectedEdges[edge.id]) {
        edgesToDelete.add(edge.id);
        edges = edges.filter(e => e.id !== edge.id);
      }
    }

    if (edgesToDelete.size <= 0) {
      return of({ edges, nodes: nodes, componentsInDag });
    }

    return forkJoin(Array.from(edgesToDelete).map(edgeId => this.journeyService.deleteJourneyDagEdge(edgeId))).pipe(
      map(() => ({ edges, nodes: nodes, componentsInDag })),
    );
  }

  @Reduce()
  onDeleteSelected(state: DagState, { edges, nodes, componentsInDag }: {
    edges: JourneyDagEdge[];
    nodes: DagCompleteNode[],
    componentsInDag: { [componentId: string]: boolean }
  }): DagState {
    return {
      ...state,
      edges,
      nodes,
      componentsInDag,
      selectedEdges: {},
      selectedNodes: {},
    };
  }

  @Effect('concatMap')
  getDagNodeDetail(projectId: string, instanceId: string, node: JourneyDagNode): Observable<[ EntityListResponse<TestOutcomeItem>, EntityListResponse<Run>, JourneyDagNode, EntityListResponse<EventType>, EntityListResponse<Schedule> ]> {
    return forkJoin([
      this.projectService.getAllTests({
        parentId: projectId,
        filters: { instance_id: instanceId, component_id: node.component.id }
      }),
      node.component.type === ComponentType.BatchPipeline ? this.runsService.findAll({
        parentId: projectId,
        filters: { instance_id: instanceId, pipeline_id: node.component.id }
      }) : of(null),
      of(node),
      node.component.type === ComponentType.Dataset ? this.projectService.getAllEvents({
        parentId: projectId,
        filters: {
          instance_id: instanceId,
          component_id: node.component.id,
          event_type: EventTypes.DatasetOperationEvent.toString()
        }
      }) : of(null),
      node.component.type === ComponentType.Dataset ? this.componentsService.getSchedules(node.component.id) : of(null)
    ]);
  }

  @Reduce()
  onGetDagNodeDetail(state: DagState, [ { entities: tests }, runs, node, events, schedules ]: [ EntityListResponse<TestOutcomeItem>, EntityListResponse<Run>, JourneyDagNode, EntityListResponse<EventType>, EntityListResponse<Schedule> ]): DagState {
    let componentRuns = runs ? runs.entities : [];
    let componentEvents = events ? events.entities : [];

    const runs_summary = getSummary(componentRuns.map(run => ({ status: run.status.toString() }))) as unknown as InstanceRunSummary[];
    const tests_summary = getSummary(tests.map(run => ({ status: run.status.toString() }))) as unknown as InstanceTestSummary[];
    let status = mostImportantStatus([ ...componentRuns, ...tests ]);

    if (node.component.type === ComponentType.Dataset) {
      status = getDatasetStatus(componentEvents, tests, schedules?.entities ?? []);
    }

    const nodeDetails: InstanceDagNode = {
      ...node,
      runs_summary,
      runs_count: componentRuns.length,
      status,
      tests_count: tests.length,
      tests_summary,
      events: componentEvents
    };

    const nodes = state.nodes;
    const nodeIdx = nodes.findIndex(n => n.info.component.id === node.component.id);

    if (nodeIdx > -1) {
      nodes[nodeIdx] = { ...nodes[nodeIdx], details: nodeDetails };
      return { ...state, nodes };
    }

    return state;
  }

  private hasCycles(nodes: JourneyDagNode[], edges: JourneyDagEdge[]): boolean {
    const positionMap = new Map();
    const adjencentNodes: { [nodeId: string]: string[] } = {};

    for (const node of nodes) {
      if (!adjencentNodes[node.component.id]) {
        adjencentNodes[node.component.id] = [];
      }
    }

    for (const edge of edges) {
      if (edge.from) {
        adjencentNodes[edge.from].push(edge.to);
      }
    }

    for (const [ index, nodeId ] of this.topologicalSort(nodes, adjencentNodes).entries()) {
      positionMap.set(nodeId, index);
    }

    for (const node of nodes) {
      const nodeId = node.component.id;
      for (const adjacentNode of adjencentNodes[nodeId]) {
        if ((positionMap.get(nodeId) ?? 0) > (positionMap.get(adjacentNode) ?? 0)) {
          return true;
        }
      }
    }

    return false;
  }

  private topologicalSort(nodes: JourneyDagNode[], adjencentNodes: { [edgeId: string]: string[] }): string[] {
    const sortingStack: string[] = [];
    const visitedNodes: { [nodeId: string]: boolean } = {};

    for (const node of nodes) {
      visitedNodes[node.component.id] = false;
    }

    for (const node of nodes) {
      if (!visitedNodes[node.component.id]) {
        this.topologicalSortInPlace(node.component.id, adjencentNodes, visitedNodes, sortingStack);
      }
    }

    return sortingStack.reverse();
  }

  private topologicalSortInPlace(nodeId: string, adjencentNodes: { [edgeId: string]: string[] }, visitedNodes: {
    [nodeId: string]: boolean
  }, stack: string[]): void {
    visitedNodes[nodeId] = true;

    for (const adjacentNodeId of adjencentNodes[nodeId]) {
      if (!visitedNodes[adjacentNodeId]) {
        this.topologicalSortInPlace(adjacentNodeId, adjencentNodes, visitedNodes, stack);
      }
    }

    stack.push(nodeId);
  }
}
