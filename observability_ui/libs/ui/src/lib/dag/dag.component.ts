import { AfterViewInit, Component, ContentChild, ContentChildren, ElementRef, EventEmitter, Inject, Input, Output, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';
import { curveLinear, line } from 'd3';
import { Dag, DagNode, coordCenter, dagConnect, decrossTwoLayer, layeringLongestPath, sugiyama, twolayerAgg } from 'd3-dag';
import { Point } from 'd3-dag/dist/dag';
import { D3DragEvent, drag } from 'd3-drag';
import { Selection, select, selectAll } from 'd3-selection';
import { D3ZoomEvent, ZoomBehavior, ZoomTransform, zoom, zoomIdentity } from 'd3-zoom';
import { BehaviorSubject, SchedulerLike, Subject, combineLatest, debounceTime, map, pairwise, startWith } from 'rxjs';
import { DagEdgeDirective } from './dag-edge.directive';
import { DagLegendDirective } from './dag-legend.directive';
import { DagNodeDirective } from './dag-node.directive';
import { DagOrientation, DraggedDagEdge } from './dag.model';

type HTMLElementWithChildren = HTMLElement & { children: HTMLElementWithChildren[] };

interface SimpleZoom {
  x: number;
  y: number;
  k: number;

}

@Component({
  selector: 'dag',
  templateUrl: 'dag.component.html',
  styleUrls: [ 'dag.component.scss' ],
})
export class DagComponent implements AfterViewInit {
  @Input() selectable = false;
  @Input() nodeSize: [ number, number ] = [ 100, 100 ];
  @Input() namespace!: string;
  @Input() restoreFromLocalStorage: boolean = false;
  @Input() persistOnLocalStorage: boolean = false;
  @ContentChild(DagLegendDirective) dagLegend?: ElementRef;

  @ContentChildren(DagNodeDirective) dagNodes!: QueryList<DagNodeDirective>;

  @ContentChildren(DagEdgeDirective) dagEdges!: QueryList<DagEdgeDirective>;

  @ViewChildren('nodeObject') private nodes!: QueryList<ElementRef>;

  @ViewChild('canvas', { static: true }) private canvasEl!: ElementRef<SVGElement>;
  @ViewChild('graph', { static: true }) private graphEl!: ElementRef<SVGElement>;
  @ViewChildren('nodeDots') private nodeDotsElements!: QueryList<ElementRef>;


  @Output() addEdge: EventEmitter<{ from: string, to: string }> = new EventEmitter<{ from: string, to: string }>();
  @Output() nodeSelected: EventEmitter<{ node?: DagNodeDirective, multiple: boolean }> = new EventEmitter<{
    node?: DagNodeDirective,
    multiple: boolean
  }>();
  @Output() edgeSelected: EventEmitter<{ edge?: DagEdgeDirective, multiple: boolean }> = new EventEmitter<{
    edge?: DagEdgeDirective,
    multiple: boolean
  }>();
  @Output() renderError: EventEmitter<string | undefined> = new EventEmitter();

  zoom$: BehaviorSubject<SimpleZoom> = new BehaviorSubject({ x: 0, y: 0, k: 1});
  orientation$: BehaviorSubject<DagOrientation> = new BehaviorSubject<DagOrientation>(DagOrientation.Horizontal);
  draggedEdge$: BehaviorSubject<DraggedDagEdge | null> = new BehaviorSubject<DraggedDagEdge | null>(null);

  readonly minZoomScale: number = 0.1;
  readonly maxZoomScale: number = 2;
  private readonly zoomStep = 0.1;
  private readonly lineFn = line<{ x: number; y: number }>()
    .curve(curveLinear)
    .x((node) => node.x)
    .y((node) => node.y);

  private zoomBehavior: ZoomBehavior<SVGElement, unknown> = zoom<SVGElement, unknown>();

  private refresh$: Subject<void> = new Subject<void>();
  private dagNodes$ = new Subject<DagNodeDirective[]>();
  private dagEdges$ = new Subject<DagEdgeDirective[]>();

  private nodeChanges$ = this.dagNodes$.pipe(
    pairwise(),
    map(([previous, current]) => this.detectChanges([previous, current]))
  );

  constructor(
    @Inject(rxjsScheduler) private scheduler: SchedulerLike,
  ) {

    this.nodeChanges$.pipe(
      debounceTime(100, this.scheduler),
      takeUntilDestroyed(),
    ).subscribe((diff) => {

      for (const removed of diff.removed) {
        this.removeStoredPosition(removed);
      }

      if (diff.added.length > 0 && this.selectable) {
        this.enableDrag();
        this.enableEdgeDrag();
      }
    });

    let inited = false;

    combineLatest([
      this.orientation$,
      this.dagEdges$.pipe(
        startWith([]),
      ),
      this.dagNodes$,
      this.refresh$.pipe(
        startWith(true),
      ),
    ]).pipe(
      debounceTime(100, this.scheduler), // this is saving us from a few annoying ExpressionChangedAfter... errors
      takeUntilDestroyed(),
    ).subscribe(([orientation,  edges, nodes]) => {
        const nodeElements = this.nodes.toArray().map((el: ElementRef<HTMLElementWithChildren>) => el.nativeElement);


        if (!inited) {
          this.enableZoom();


          if (this.selectable) {
            this.enableDrag();
            this.enableEdgeDrag();

          }

          this.updateNodesSize(nodes, nodeElements); // this ensures nodes have height/width to use when aligning the floating ones
          this.updateNodesPosition(nodes, edges, orientation); // this ensures nodes have x/y when aligning the floating ones
          this.alignFloatingNodes(orientation, nodes);

          setTimeout(() => {
            // add some slack otherwise zoom to fit won't work
            this.initZoom();
          });

          inited = true;

        } else {

          this.updateNodesSize(nodes, nodeElements);
          this.updateNodesPosition(nodes, edges, orientation);
        }

      });
  }

  /* istanbul ignore next */
  ngAfterViewInit(): void {

    this.dagEdges.changes.pipe(
      map((list) => list.toArray()),
    ).subscribe(this.dagEdges$);

    this.dagNodes.changes.pipe(
      map((list) => list.toArray()),
    ).subscribe(this.dagNodes$);

  }

  initZoom(): void {
    if (this.canvasEl && this.dagNodes?.length > 0) {
      const svgEl = this.canvasEl.nativeElement as SVGElement;

      const storedZoom = this.getStoredZoom();

      if (storedZoom) {
        const {x, y, k} = storedZoom;
        this.zoomBehavior.transform(select(svgEl), zoomIdentity.translate(x, y).scale(k));
      } else {

        this.zoomToFit();
      }
    }
  }

  zoomIn(): void {
    const currentZoom = this.zoom$.getValue();
    const scale = currentZoom.k + this.zoomStep;
    if (scale < this.maxZoomScale) {
      this.zoom$.next({ ...currentZoom, k: scale });
      this.zoomBehavior.scaleTo(select(this.canvasEl.nativeElement), scale);
    }
  }

  zoomOut(): void {
    const currentZoom = this.zoom$.getValue();
    const scale = currentZoom.k - this.zoomStep;
    if (scale > this.minZoomScale) {
      this.zoom$.next({ ...currentZoom, k: scale });
      this.zoomBehavior.scaleTo(select(this.canvasEl.nativeElement), scale);
    }
  }

  zoomToFit() {

    const svgEl = this.canvasEl.nativeElement as SVGElement;
    const graphEl = this.graphEl.nativeElement as SVGGraphicsElement;

    const graphBounds = graphEl.getBBox();

    const fullWidth = svgEl.clientWidth;
    const graphWidth = graphBounds.width;
    const fullHeight = svgEl.clientHeight;
    const graphHeight = graphBounds.height;

    const midX = graphBounds.x + (graphWidth / 2);
    const midY = graphBounds.y + (graphHeight / 2);

    if (graphWidth === 0 || graphHeight === 0) {
      return;
    }

    const newScale = 0.85 / Math.max(graphWidth / fullWidth, graphHeight / fullHeight);
    const scale = Math.min(Math.max(newScale, this.minZoomScale), this.maxZoomScale);

    const translationX = fullWidth / 2 - scale * midX;
    const translationY = fullHeight / 2 - scale * midY;

    this.zoom$.next({ x: translationX, y: translationY, k: scale });
    this.zoomBehavior.transform(select(svgEl), zoomIdentity.translate(translationX, translationY).scale(scale));

  }

  setOrientation(orientation: DagOrientation): void {
    this.orientation$.next(orientation);
  }

  refresh(): void {
    this.refresh$.next();
  }

  selectNode(node: DagNodeDirective, event: MouseEvent) {
    event.stopPropagation();

    if (this.selectable) {
      const multiple = (event.shiftKey || event.ctrlKey || event.metaKey);

      if (!multiple) {
        this.dagEdges.forEach(e => e.selected = false);
      }

      this.nodeSelected.emit({ node, multiple });
    }
  }

  selectEdge(edge: DagEdgeDirective, event: MouseEvent, edgeElement: HTMLElement) {
    event.stopPropagation();
    if (this.selectable) {
      const multiple = (event.shiftKey || event.ctrlKey || event.metaKey);

      if (!multiple) {
        this.dagEdges.filter(e => e !== edge).forEach(e => e.selected = false);
      }

      edge.selected = !edge.selected;
      this.edgeSelected.emit({ edge, multiple });
      select(edgeElement).raise();
    }
  }

  onClickCanvas(event: MouseEvent) {
    // This won't be triggered when clicking an edge or a node
    if (event.target === this.canvasEl?.nativeElement) {
      this.dagEdges.forEach(dagEdge => dagEdge.selected = false);

      this.nodeSelected.emit({ node: undefined, multiple: false });
      this.edgeSelected.emit({ edge: undefined, multiple: false });
    }
  }

  /* istanbul ignore next */
  private enableZoom(): void {
    let currentTransform: ZoomTransform = zoomIdentity;
    const { width, height } = this.canvasEl.nativeElement.getBoundingClientRect();

    select(this.canvasEl.nativeElement)
      .call(
        this.zoomBehavior
          .scaleExtent([ this.minZoomScale, this.maxZoomScale ])
          .extent([ [ 0, 0 ], [ width, height ] ])
          .on('zoom', ($event: D3ZoomEvent<SVGElement, unknown>) => {
            const { transform } = $event;
            if (currentTransform.k !== transform.k ||
                currentTransform.x !== transform.x ||
                currentTransform.y !== transform.y
            ) {
              currentTransform = transform;
              this.zoom$.next(transform);
              this.storeZoom(transform);
            }

            select(this.graphEl?.nativeElement).attr('transform', transform.toString());
          })
      );
  }

  /* istanbul ignore next */
  private enableDrag(): void {
    const selectNodeFn = this.selectNode.bind(this);
    const redispatchClickEventFn = this.redispatchClickEvent.bind(this);

    const dragBehavior = drag<SVGElement, DagNodeDirective>()
      .on('start', function(event, node): void {
        select(this).raise(); // NOTE (1): This forces the user to click twice in order to select a node because https://github.com/w3c/uievents/issues/141 ...
        selectNodeFn(node, event.sourceEvent); // NOTE (2): ... and, this is the workaround

        try {
          // NOTE (3): the workaround above works fine for selecting nodes but still is as if the event was never dispatched, below we re-dispatch the event
          // after 'raising' the element –– Some clicks failed to be re-dispatched so catch and ignore
          redispatchClickEventFn(event.sourceEvent as MouseEvent);
        } catch {
          ;
        }
        node.wrapperClass = 'dragging';
      })
      .on('drag', (event, node) => {
        node.x = event.x;
        node.y = event.y;

        for (const edge of node.outgoing) {
          this.repositionEdgeAtSource(edge, node);
        }

        for (const edge of node.incoming) {
          this.repositionEdgeAtTarget(edge, node);
        }
      })
      .on('end', (_, node) => {
        node.wrapperClass = '';
        this.storeNodePosition(node);

      });

    this.applyBehavior(this.nodes, dragBehavior);

  }

  /* istanbul ignore next */
  private redispatchClickEvent(original: MouseEvent): void {
    if (original.type !== 'mousedown' || !original.target) {
      return;
    }

    const newEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true,
      button: original.button,
      buttons: original.buttons,
      clientX: original.clientX,
      clientY: original.clientY,
      movementX: original.movementX,
      movementY: original.movementY,
      screenX: original.screenX,
      screenY: original.screenY,
      relatedTarget: original.relatedTarget,
      ctrlKey: original.ctrlKey,
      shiftKey: original.ctrlKey,
      metaKey: original.metaKey
    });
    original.target.dispatchEvent(newEvent);
  }

  /* istanbul ignore next */
  private enableEdgeDrag(): void {
    const dragEdgeBehavior = drag<SVGElement, DagNodeDirective>()
      .on('start', ({ sourceEvent, subject }: D3DragEvent<SVGElement, DagNodeDirective, DagNodeDirective>) => {
        const target = (sourceEvent as DragEvent).target as SVGElement;
        const targetCx = +(target.getAttribute('cx') ?? 0);
        const targetCy = +(target.getAttribute('cy') ?? 0);
        const sourceNodeId = target.getAttribute('data-node') as string;

        this.draggedEdge$.next({
          points: [ { x: subject.x + targetCx, y: subject.y + targetCy } ],
          offset: { x: targetCx, y: targetCy },
          path: '',
          sourceNodeId,
        });
      })
      .on('drag', ({ x, y }: D3DragEvent<SVGElement, DagNodeDirective, DagNodeDirective>) => {
        const draggedEdge = this.draggedEdge$.getValue();
        if (draggedEdge) {
          const points = [ draggedEdge.points[0], { x: x + draggedEdge.offset.x, y: y + draggedEdge.offset.y } ];
          this.draggedEdge$.next({ ...draggedEdge, points, path: this.lineFn(points) ?? '' });
        }
      })
      .on('end', (event: D3DragEvent<SVGElement, DagNodeDirective, DagNodeDirective>) => {
        const target = (event.sourceEvent as DragEvent).target as HTMLElement;
        const draggedEdge = this.draggedEdge$.getValue();
        if (draggedEdge && target) {
          const targetNodeId = this.getTargetNodeId(target);
          if (targetNodeId && draggedEdge.sourceNodeId !== targetNodeId) {
            this.addEdge.emit({ from: draggedEdge.sourceNodeId, to: targetNodeId });
          }
        }
        this.draggedEdge$.next(null);
      });

    this.applyBehavior(this.nodeDotsElements, dragEdgeBehavior);

  }

  /* istanbul ignore next */
  private getTargetNodeId(target: HTMLElement): string | null {
    if (!target) {
      return null;
    }
    if (target.tagName === 'g' || target.hasAttribute('data-node')) {
      return target.getAttribute('data-node');
    }
    return this.getTargetNodeId(target.parentElement as HTMLElement);
  }

  /* istanbul ignore next */
  private applyBehavior(queryList: QueryList<ElementRef>, behavior: (selection: Selection<SVGElement, DagNodeDirective, any, any>) => void): void {

    const nativeElements = queryList.toArray().map((el: ElementRef<SVGElement>) => el.nativeElement);
    const selection = selectAll(nativeElements).data(this.dagNodes.toArray());
    behavior(selection);
  }

  /* istanbul ignore next */
  private updateNodesSize(nodes: DagNodeDirective[], nodeElements: HTMLElementWithChildren[]): void {
    selectAll(nodeElements.map(e => e.children[0]))
      .data(nodes)
      .attr('width', (node, i, elements) => {
        node.width = elements[i].children[0].offsetWidth;
        return node.width;
      })
      .attr('height', (node, i, elements) => {
        node.height = elements[i].children[0].offsetHeight;
        return node.height;
      });
  }

  // disabling coverage collection for now; see comment below on `layout` funtion
  /* istanbul ignore next */
  private updateNodesPosition(nodes: DagNodeDirective[], edges: DagEdgeDirective[], orientation: DagOrientation): void {
    const nodesMap: Map<string, DagNodeDirective> = nodes.reduce((map, node) => map.set(node.name, node), new Map());

    try {
      const nodeSize: [ number, number ] = orientation === DagOrientation.Horizontal ? this.nodeSize : [ ...this.nodeSize ].reverse() as [ number, number ];

      const baseLayout = sugiyama()
        .nodeSize((node: DagNode<DagNodeDirective, DagEdgeDirective> | undefined): [ number, number ] => node === undefined ? [ 0, 0 ] : nodeSize)
        .layering(layeringLongestPath())
        .decross(decrossTwoLayer().order(twolayerAgg()))
        .coord(coordCenter());

      const create = dagConnect()
        .nodeDatum((id) => nodesMap.get(id) as DagNodeDirective)
        .sourceId((link: DagEdgeDirective) => link.fromNode)
        .targetId((link: DagEdgeDirective) => link.toNode);

      const graph = create(edges);

      const layout = (dag: Dag<DagNodeDirective, DagEdgeDirective>) => {

        // this logic should probably be moved when we
        // implement the different types of auto-layouting
        // then probably part of the below can be tested
        let { width, height } = baseLayout(dag);
        if (orientation === DagOrientation.Horizontal) {
          for (const node of dag) {
            [ node.x, node.y ] = [ node.y, node.x ];
          }

          for (const { points } of dag.ilinks()) {
            for (const point of points) {
              // eslint-disable-next-line @typescript-eslint/ban-ts-comment
              // @ts-ignore
              [ point.x, point.y ] = [ point.y, point.x ];
            }
          }

          [ width, height ] = [ height, width ];
        }

        for (const { x = 0, y = 0, data: node } of dag) {

          const storedPosition = this.getStoredPosition(node);
          node.x = storedPosition?.x ?? x;
          node.y = storedPosition?.y ?? y;
          node.clearEdges();
        }

        for (const { source, target, points, data } of dag.ilinks()) {
          data.points = this.addAMiddlePoint([ points[0], points.slice(-1)[0] ]);

          this.repositionEdgeAtSource(data, source.data);
          this.repositionEdgeAtTarget(data, target.data);

          source.data.addOutgoingEdge(data);
          target.data.addIncomingEdge(data);
        }

      };

      layout(graph);

      // this.changeDetectorRef.detectChanges();
      this.renderError.emit(undefined);
    } catch (error) {
      console.error(error);

      // this.renderError.emit('The system has encountered an error rendering the graph.');
    }
  }

  /* istanbul ignore next */
  private repositionEdgeAtSource(edge: DagEdgeDirective, source: DagNodeDirective): void {
    const orientation = this.orientation$.getValue();
    edge.points[0] = source.bottom;
    if (orientation === DagOrientation.Horizontal) {
      edge.points[0] = source.right;
    }

    edge.points = this.addAMiddlePoint([ edge.points[0], edge.points[edge.points.length - 1] ]);
    edge.path = this.lineFn(edge.points) ?? '';
  }

  /* istanbul ignore next */
  private repositionEdgeAtTarget(edge: DagEdgeDirective, target: DagNodeDirective): void {
    const orientation = this.orientation$.getValue();
    edge.points[edge.points.length - 1] = target.top;
    if (orientation === DagOrientation.Horizontal) {
      edge.points[edge.points.length - 1] = target.left;
    }

    edge.points = this.addAMiddlePoint([ edge.points[0], edge.points[edge.points.length - 1] ]);
    edge.path = this.lineFn(edge.points) ?? '';
  }

  /* istanbul ignore next */
  private addAMiddlePoint([ source, target ]: Point[]): Point[] {
    return [ source, { x: (source.x + target.x) / 2, y: (source.y + target.y) / 2 }, target ];
  }

  /* istanbul ignore next */
  private alignFloatingNodes(orientation: DagOrientation, nodes: DagNodeDirective[]): void {

    const looseNodes = nodes.filter(({incoming, outgoing}) => incoming.length + outgoing.length === 0);

    const getStartingPosition = () => nodes
      .filter(n => n.incoming.length + n.outgoing.length > 0)
      .sort((a, b) => {
        return  orientation === DagOrientation.Horizontal ? (a.x - b.x) : (a.y - b.y);
      })
      .reduce(([ x, y ], node) => {

        if (orientation === DagOrientation.Horizontal) {
          return [ x || node.x, (x || node.x) === x ? Math.max(y, node.y + node.height) : y ];
        } else {
          return [ node.y === y ? Math.max(x, node.x + node.width) : x, y || node.y ];
        }

      }, [ 0, 0 ]);


    const [ startingX, startingY ] = getStartingPosition();

    const previuoPosition = {x:0, y:0};


    const isHorizontal = orientation === DagOrientation.Horizontal;

    for (const node of looseNodes) {
      if (!node) continue;

      // check if node has stored position
      const storedPosition = this.getStoredPosition(node);
      if (storedPosition) {
        node.x = storedPosition.x;
        node.y = storedPosition.y;
      } else {
        node.x = isHorizontal ? startingX : previuoPosition.x + node.width + 50;
        node.y = isHorizontal ? previuoPosition.y + node.height + 50 : startingY;

        previuoPosition.y = node.y;
        previuoPosition.x = node.x;
        this.storeNodePosition(node);
      }

    }

  }

  /* istanbul ignore next */
  private getStoredPosition(node: DagNodeDirective): {x: number; y: number} | undefined {

    if (this.restoreFromLocalStorage && this.namespace) {

      const stored = localStorage.getItem([this.namespace, node.name].join(':'));
      if (stored) {
        return JSON.parse(stored);
      }

    }
    return undefined;
  }

  /* istanbul ignore next */
  private storeNodePosition(node: DagNodeDirective) {
    if (this.persistOnLocalStorage && this.namespace) {
      localStorage.setItem([this.namespace, node.name].join(':'), JSON.stringify({x: node.x, y: node.y}));
    }
  }

  /* istanbul ignore next */
  private removeStoredPosition(node: DagNodeDirective) {
    if (this.persistOnLocalStorage && this.namespace) {
      localStorage.removeItem([this.namespace, node.name].join(':'));
    }
  }

  /* istanbul ignore next */
  private getStoredZoom(): SimpleZoom|undefined {
    if (this.restoreFromLocalStorage && this.namespace) {
      const stored = localStorage.getItem([this.namespace, 'zoom'].join(':'));
      if (stored) {
        return JSON.parse(stored);
      }
    }
    return undefined;
  }

  /* istanbul ignore next */
  private storeZoom(zoom: SimpleZoom) {
    if (this.persistOnLocalStorage && this.namespace) {
      localStorage.setItem([this.namespace, 'zoom'].join(':'), JSON.stringify(zoom));
    }
  }

  private detectChanges([previous, current]: [DagNodeDirective[], DagNodeDirective[]]): { added: DagNodeDirective[]; removed: DagNodeDirective[]; } {
    const added: DagNodeDirective[] = [];
    const removed: DagNodeDirective[] = [];

    for (const node of current) {
      const idx = previous.findIndex(({name}) => name === node.name) ;
      if (idx < 0) {
        // node is not in previous array hence is new
        added.push(node);
      }
    }

    for (const node of previous) {
      const idx = current.findIndex(({name}) => name === node.name);
      if (idx < 0) {
        // node is not in current array hence has been deleted
        removed.push(node);
      }
    }

    return {
      added,
      removed,
    };
  }
}
