/* istanbul ignore file */

import { Directive, Input, Signal, TemplateRef, WritableSignal, computed, signal } from '@angular/core';

import { Position } from './gantt-chart.model';


@Directive({
  selector: '[ganttBar]',
})
export class GanttBarDirective {
  @Input('ganttBar') id!: string;
  @Input() ganttBarLabel!: string;
  @Input() set ganttBarStart(value: Date) {
    this._start.set(value);
  };
  @Input() set ganttBarEnd(value: Date) {
    this._end.set(value);
  };
  @Input() ganttBarGroupBy!: string;
  @Input() ganttBarParent?: string;
  @Input() ganttBarContext?: object;

  public get label() { return this.ganttBarLabel; };
  public get groupBy() { return this.ganttBarGroupBy; };
  public get parent() { return this.ganttBarParent; };
  public get nested() { return !!this.ganttBarParent; };
  public get context() { return this.ganttBarContext; };

  public start: Signal<Date> = computed(() => this._start() as Date);
  public end: Signal<Date> = computed(() => this._end() as Date);

  public position: Position | undefined;
  public left: WritableSignal<string> = signal('0px');
  public width: WritableSignal<string> = signal('0px');
  public display: WritableSignal<string> = signal('none');

  private _start: WritableSignal<Date | undefined> = signal(undefined);
  private _end: WritableSignal<Date | undefined> = signal(undefined);

  constructor(public template: TemplateRef<any>) {}
}
