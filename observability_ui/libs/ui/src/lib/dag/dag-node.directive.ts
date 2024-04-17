/* eslint-disable @typescript-eslint/ban-ts-comment */
import { Directive, Input, TemplateRef } from '@angular/core';
import { DagEdgeDirective } from './dag-edge.directive';

@Directive({
  selector: '[dagNode]',
})
export class DagNodeDirective {
  @Input('dagNode') public name!: string;

  @Input()
  public set dagNodeCenterX(value: number) {
    this.centerX = value;
  }

  @Input()
  public set dagNodeCenterY(value: number) {
    this.centerY = value;
  }

  @Input()
  public set dagNodeWrapperClass(value: string) {
    this.wrapperClass = value ?? '';
  }

  public x: number = 0;
  public y: number = 0;

  public width: number = 0;
  public height: number = 0;

  public centerX?: number;
  public centerY?: number;
  public wrapperClass: string = '';

  public readonly incoming: DagEdgeDirective[] = [];
  public readonly outgoing: DagEdgeDirective[] = [];

  get left(): { x: number, y: number } {
    const diff = this.centerY ?? this.height / 2;
    return { x: this.x, y: this.y + diff };
  }

  get top(): { x: number, y: number } {
    const diff = this.centerX ?? this.width / 2;
    return { x: this.x + diff, y: this.y };
  }

  get right(): { x: number, y: number } {
    const diff = this.centerY ?? this.height / 2;
    return { x: this.x + this.width, y: this.y + diff };
  }

  get bottom(): { x: number, y: number } {
    const diff = this.centerX ?? this.width / 2;
    return { x: this.x + diff, y: this.y + this.height };
  }

  constructor(public template: TemplateRef<any>) {}

  public addIncomingEdge(edge: DagEdgeDirective): void {
    this.incoming.push(edge);
  }

  public addOutgoingEdge(edge: DagEdgeDirective): void {
    this.outgoing.push(edge);
  }

  public clearEdges(): void {
    this.incoming.splice(0, this.incoming.length);
    this.outgoing.splice(0, this.outgoing.length);
  }
}
