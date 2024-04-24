export enum DagOrientation {
  Horizontal = 'HORIZONTAL',
  Vertical = 'VERTICAL',
}

export interface DagEdge {
  path: string;
  points: Array<{x: number; y: number}>;
}

export interface DraggedDagEdge extends DagEdge {
  offset: { x: number, y: number };
  sourceNodeId: string;
}
