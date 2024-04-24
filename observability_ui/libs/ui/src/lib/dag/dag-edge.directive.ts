import { Directive, Input } from '@angular/core';
import { DagEdge } from './dag.model';

@Directive({
  selector: 'dag-edge',
})
export class DagEdgeDirective implements DagEdge {
  @Input() public id!: string;
  @Input() public fromNode!: string;
  @Input() public toNode!: string;

  public path: string = '';
  public selected: boolean = false;
  public points: Array<{x: number; y: number}> = [];
}
