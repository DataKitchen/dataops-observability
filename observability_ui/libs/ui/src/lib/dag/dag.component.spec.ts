import { ElementRef, QueryList } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MockComponent } from 'ng-mocks';
import { Subject } from 'rxjs';
import { DagActionsComponent } from './dag-actions/dag-actions.component';
import { DagEdgeDirective } from './dag-edge.directive';
import { DagNodeDirective } from './dag-node.directive';
import { DagComponent } from './dag.component';
import { DagOrientation } from './dag.model';

const zoomBehaviorMock: any = jest.fn();
zoomBehaviorMock.apply = jest.fn();
zoomBehaviorMock.translateTo = jest.fn();
zoomBehaviorMock.scaleTo = jest.fn();
zoomBehaviorMock.transform = jest.fn();
zoomBehaviorMock.scaleExtent = jest.fn().mockImplementation(() => zoomBehaviorMock);
zoomBehaviorMock.extent = jest.fn().mockImplementation(() => zoomBehaviorMock);
zoomBehaviorMock.on = jest.fn().mockImplementation(() => zoomBehaviorMock);

const dagConnectOperatorMock: any = jest.fn();
dagConnectOperatorMock.nodeDatum = jest.fn().mockImplementation(() => dagConnectOperatorMock);
dagConnectOperatorMock.sourceId = jest.fn().mockImplementation(() => dagConnectOperatorMock);
dagConnectOperatorMock.targetId = jest.fn().mockImplementation(() => dagConnectOperatorMock);

const sugiyamaOperatorMock: any = jest.fn();
sugiyamaOperatorMock.nodeSize = jest.fn().mockImplementation(() => sugiyamaOperatorMock);
sugiyamaOperatorMock.layering = jest.fn().mockImplementation(() => sugiyamaOperatorMock);
sugiyamaOperatorMock.decross = jest.fn().mockImplementation(() => sugiyamaOperatorMock);
sugiyamaOperatorMock.coord = jest.fn().mockImplementation(() => sugiyamaOperatorMock);


jest.mock('d3', () => {
  const original = jest.requireActual('d3');
  return {
    ...original,
    dagConnect: () => dagConnectOperatorMock,
    sugiyama: () => sugiyamaOperatorMock,
    zoom: () => zoomBehaviorMock,
  };
});

describe('DAG Component', () => {
  const width = 200;
  const height = 100;

  let nodesChangesSubject: Subject<never>;

  let dagNodes: DagNodeDirective[] = [];
  let dagEdges: DagEdgeDirective[] = [];
  let nodeElements: Array<ElementRef<any>> = [];

  let component: DagComponent;
  let fixture: ComponentFixture<DagComponent>;

  let testScheduler: TestScheduler;

  beforeEach(() => {

    testScheduler = new TestScheduler();

    TestBed.configureTestingModule({
      imports: [
        MatProgressSpinnerModule,
      ],
      declarations: [
        DagComponent,
        TranslatePipeMock,
        MockComponent(DagActionsComponent),
      ],
      providers: [
        {
          provide: rxjsScheduler,
          useValue: testScheduler,
        }
      ],
    });

    fixture = TestBed.createComponent(DagComponent);
    component = fixture.componentInstance;

    dagEdges = [
      { fromNode: 'A', toNode: 'B' },
      { fromNode: 'A', toNode: 'C' },
      { fromNode: 'B', toNode: 'D' },
      { fromNode: 'C', toNode: 'D' },
    ] as DagEdgeDirective[];

    dagNodes = [
      { x: 0, y: 0, width: 0, height: 0, name: 'A', incoming: [], outgoing: [ dagEdges[0], dagEdges[1] ], addIncomingEdge: jest.fn(), addOutgoingEdge: jest.fn() } as unknown as DagNodeDirective,
      { x: 0, y: 0, width: 0, height: 0, name: 'B', incoming: [ dagEdges[0] ], outgoing: [ dagEdges[2] ], addIncomingEdge: jest.fn(), addOutgoingEdge: jest.fn() } as unknown as DagNodeDirective,
      { x: 0, y: 0, width: 0, height: 0, name: 'C', incoming: [ dagEdges[1] ], outgoing: [ dagEdges[3] ], addIncomingEdge: jest.fn(), addOutgoingEdge: jest.fn() } as unknown as DagNodeDirective,
      { x: 0, y: 0, width: 0, height: 0, name: 'D', incoming: [ dagEdges[2], dagEdges[3] ], outgoing: [], addIncomingEdge: jest.fn(), addOutgoingEdge: jest.fn() } as unknown as DagNodeDirective,
    ] as DagNodeDirective[];

    nodeElements = [
      { children: [ {setAttribute: () => ({}), children: [ {offsetWidth: 200, offsetHeight: 60} ]} ] },
      { children: [ {setAttribute: () => ({}), children: [ {offsetWidth: 100, offsetHeight: 20} ]} ] },
      { children: [ {setAttribute: () => ({}), children: [ {offsetWidth: 150, offsetHeight: 20} ]} ] },
      { children: [ {setAttribute: () => ({}), children: [ {offsetWidth: 230, offsetHeight: 50} ]} ] },
    ].map(nativeElement => ({ nativeElement }));

    nodesChangesSubject = new Subject();

    component['canvasEl'] = {
      nativeElement: {
        style: { width: `${width}px`, height: `${height}px` },
        clientWidth: width,
        clientHeight: height,
        getBoundingClientRect: () => ({ width, height }),
      },
    } as ElementRef<any>;

    component['graphEl'] = {
      nativeElement: {
        getBBox: () => ({ width: 0, height: 0, x: 0, y: 0 }),
        setAttribute: jest.fn(),
      },
    } as ElementRef<any>;

    component.initZoom = jest.fn().mockImplementation(component.initZoom.bind(component));
    fixture.detectChanges();

    component.dagNodes = dagNodes as unknown as QueryList<DagNodeDirective>;
    component.dagNodes.toArray = () => dagNodes;
    component.dagEdges = dagEdges as unknown as QueryList<DagEdgeDirective>;
    component.dagEdges.toArray = () => dagEdges;

    component['nodes'] = {
      changes: nodesChangesSubject,
      toArray: () => nodeElements
    } as unknown as QueryList<ElementRef<any>>;

    component.nodeSelected = { emit: jest.fn() } as any;
    component.edgeSelected = { emit: jest.fn() } as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should start with horizontal orientation', () => {
    expect(component.orientation$.getValue()).toBe(DagOrientation.Horizontal);
  });

  it('should update node sizes when refreshing', () => {

    testScheduler.run(({ flush }) => {
      jest.spyOn<any, any>(component, 'updateNodesSize');

      fixture.detectChanges();
      component.refresh();
      component['dagNodes$'].next([]);
      component['dagEdges$'].next([]);
      flush();

      expect(component['updateNodesSize']).toHaveBeenCalled();

    });

  });

  describe('node changes', () => {

    it('should pass added nodes', () => {

      const addedNode = { x: 0, y: 0, width: 0, height: 0, name: 'Z', incoming: [], outgoing: [ dagEdges[0], dagEdges[1] ], addIncomingEdge: jest.fn(), addOutgoingEdge: jest.fn() } as unknown as DagNodeDirective;

      expect(component['detectChanges']([dagNodes, [...dagNodes, addedNode]])).toEqual({
        added: [addedNode],
        removed: [],
      });

    });

    it('should pass removed nodes', () => {

      // get a copy without the first element
      const lessNodes = dagNodes.slice(1);

      expect(component['detectChanges']([dagNodes, lessNodes])).toEqual({
        added: [],
        removed: [dagNodes[0]],
      });

    });

  });

  describe('zoomIn()', () => {
    beforeEach(() => {
      component.zoom$.next({ k: 1.0, x: 0, y: 0 });
    });

    it('should increase the zoom by 0.1', () => {
      component.zoomIn();
      expect(component.zoom$.getValue().k).toBe(1.1);
    });

    it('should not increase the zoom if it is at the max value of 2.0', () => {
      component.zoom$.next({ k: 2.0, x: 0, y: 0 });
      component.zoomIn();
      expect(component.zoom$.getValue().k).toBe(2.0);
    });

    it('should scale to the new zoom value', () => {
      component.zoomIn();
      expect(component['zoomBehavior'].scaleTo).toBeCalledWith(expect.any(Object), 1.1);
    });
  });

  describe('zoomOut()', () => {
    beforeEach(() => {
      component.zoom$.next({ k: 1.0, x: 0, y: 0 });
    });

    it('should descrease the zoom by 0.1', () => {
      component.zoomOut();
      expect(component.zoom$.getValue().k).toBe(0.9);
    });

    it('should not descrease the zoom if it is at the min value of 0.1', () => {
      component.zoom$.next({ k: 0.1, x: 0, y: 0});
      component.zoomOut();
      expect(component.zoom$.getValue().k).toBe(0.1);
    });

    it('should scale to the new zoom value', () => {
      component.zoomOut();
      expect(zoomBehaviorMock.scaleTo).toBeCalledWith(expect.any(Object), 0.9);
    });
  });

  describe('resetZoom()', () => {
    const canvasWidth = 300;
    const canvasHeight = 100;
    const graphWidth = 100;
    const graphHeight = 50;
    const graphX = 20;
    const graphY = 10;

    const nodes = [
      { name: 'A', x: 0, y: 50, width: 100, height: 50 },
      { name: 'B', x: 150, y: 20, width: 100, height: 50 },
      { name: 'C', x: 150, y: 80, width: 100, height: 50 },
      { name: 'D', x: 300, y: 130, width: 100, height: 50 },
    ] as DagNodeDirective[];

    beforeEach(() => {
      component['canvasEl'] = {
        nativeElement: { clientWidth: canvasWidth, clientHeight: canvasHeight },
      } as ElementRef<any>;
      component['graphEl'] = {
        nativeElement: { getBBox: () => ({ width: graphWidth, height: graphHeight, x: graphX, y: graphY }) },
      } as ElementRef<any>;
      component.dagNodes = nodes as unknown as QueryList<DagNodeDirective>;
      component.dagNodes.toArray = () => nodes;

      fixture.detectChanges();
    });

    it('should translate the DAG to the relative center of the viewport', () => {
      const scale = 0.85 / Math.max(graphWidth / canvasWidth, graphHeight / canvasHeight);
      const expectedX = canvasWidth / 2 - scale * (graphX + (graphWidth / 2));
      const expectedY = canvasHeight / 2 - scale * (graphY + (graphHeight / 2));

      component.initZoom();
      expect(zoomBehaviorMock.transform).toBeCalledWith(expect.any(Object), expect.objectContaining({ x: expectedX, y: expectedY }));
    });

    describe('#zoomToFit', () => {

      it('should scale the zoom to fit the DAG in the screen', () => {
        const expectedScale = 0.85 / Math.max(graphWidth / canvasWidth, graphHeight / canvasHeight);

        component.zoomToFit();

        expect(component.zoom$.getValue()).toEqual({ k: expectedScale, x: 31, y: -9.5});
        expect(zoomBehaviorMock.transform).toBeCalledWith(expect.any(Object), expect.objectContaining({ k: expectedScale }));
      });

    });

  });

  describe('setOrientation()', () => {
    it('should update the orientation', () => {
      component.setOrientation(DagOrientation.Vertical);
      expect(component.orientation$.getValue()).toBe(DagOrientation.Vertical);
    });
  });

  describe('selectNode()', () => {
    beforeEach(() => {
      component.selectable = true;
    });

    it('should emit nodeSelected event with node name', () => {
      const node = { name: 'A', x: 0, y: 50, width: 100, height: 50 } as DagNodeDirective;
      component.selectNode(node, { stopPropagation: jest.fn(), shiftKey: false, ctrlKey: false, metaKey: false } as any);
      expect(component.nodeSelected.emit).toHaveBeenCalledWith({ node, multiple: false });
    });
  });

  describe('selectEdge()', () => {
    beforeEach(() => {
      component.selectable = true;
    });

    it('should emit edgeSelected event', () => {
      const edgeToBeSelected: DagEdgeDirective = {
        id: 'A',
        selected: false,
        toNode: 'test-node2',
        fromNode: 'test-node',
        points: [],
        path: '',
      };
      const edgeElement = {} as any;
      component.selectEdge(edgeToBeSelected, { stopPropagation: jest.fn(), shiftKey: false, ctrlKey: false, metaKey: false } as any, edgeElement);
      expect(component.edgeSelected.emit).toHaveBeenCalledWith({ edge: edgeToBeSelected, multiple: false });
    });

    it('should toggle edge.selected', () => {
      const edgeToBeSelected: DagEdgeDirective = {
        id: 'A',
        selected: false,
        toNode: 'test-node2',
        fromNode: 'test-node',
        points: [],
        path: '',
      };
      const edgeElement = {} as any;
      component.selectEdge(edgeToBeSelected, { stopPropagation: jest.fn() } as any, edgeElement);
      expect(edgeToBeSelected.selected).toBeTruthy();
    });

    it('if no shortcut key is held, it should set all other edges to selected = false', () => {
      component.dagEdges = new QueryList();
      component.dagEdges.reset([
        { id: 'A', fromNode: 'test', toNode: 'test', points: [], path: '', selected: true },
        { id: 'B', fromNode: 'test2', toNode: 'test2', points: [], path: '', selected: false },
      ]);

      component.selectEdge((component.dagEdges.get(1) as DagEdgeDirective), { stopPropagation: jest.fn() } as any, {} as any);
      expect((component.dagEdges.get(0) as DagEdgeDirective).selected).toBeFalsy();
    });

    it('if a shortcut key is held, other selected edges should remain selected, and the current edge should be selected too', () => {
      component.dagEdges = new QueryList();
      component.dagEdges.reset([
        { id: 'A', fromNode: 'test', toNode: 'test', points: [], path: '', selected: true },
        { id: 'B', fromNode: 'test2', toNode: 'test2', points: [], path: '', selected: false }
      ]);

      component.selectEdge((component.dagEdges.get(1) as DagEdgeDirective), { stopPropagation: jest.fn(), shiftKey: true } as any, {} as any);
      expect((component.dagEdges.get(0) as DagEdgeDirective).selected).toBeTruthy();
      expect((component.dagEdges.get(1) as DagEdgeDirective).selected).toBeTruthy();
    });
  });

  describe('onClickCanvas()', () => {
    const target = {};
    beforeEach(() => {
      component['canvasEl'] = { nativeElement: target } as ElementRef<any>;
    });

    it('should set all edges selected property to false', () => {
      for (const edge of dagEdges) {
        edge.selected = true;
      }
      component.onClickCanvas({ target } as any);

      expect(dagEdges.map(e => e.selected)).toEqual(Array(dagEdges.length).fill(false));
    });

    it('should emit node selected with undefined and multiple flag off', () => {
      component.onClickCanvas({ target } as any);
      expect(component.nodeSelected.emit).toBeCalledWith({ node: undefined, multiple: false });
    });

    it('should emit edge selected with undefined and multiple flag off', () => {
      component.onClickCanvas({ target } as any);
      expect(component.edgeSelected.emit).toBeCalledWith({ edge: undefined, multiple: false });
    });

    it('should do nothing if target is not the svg element', () => {
      for (const edge of dagEdges) {
        edge.selected = true;
      }

      component.onClickCanvas({ target: {} } as any);
      expect(dagEdges.map(e => e.selected)).toEqual(Array(dagEdges.length).fill(true));
      expect(component.nodeSelected.emit).not.toBeCalled();
      expect(component.edgeSelected.emit).not.toBeCalled();
    });
  });

});
