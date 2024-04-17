import { Component, effect, HostBinding } from '@angular/core';
import { GanttBarDirective } from './gantt-bar.directive';
import { GanttChartComponent } from './gantt-chart.component';

@Component({
  selector: 'gantt-task',
  template: `
    <ng-content></ng-content>
    <div #progressOverlay
      [style.left]="progressOffset"
      [style.width]="progressWidth"
      [style.display]="display"
      class="progress-overlay"
    ></div>
  `,
  styles: [ `
    :host {
      position: absolute !important;

      height: 18px;
      min-width: 5px;
      border-radius: 2px;
    }

    :host.nested {
      height: 8px;
    }

    .progress-overlay {
      position: relative;
      background: #9e9e9e;
      border-top-right-radius: 2px;
      border-bottom-right-radius: 2px;
    }
  ` ],
})
export class GanttTaskComponent {
  @HostBinding('style.left') left: string = '0px';
  @HostBinding('style.width') width: string = '0px';
  @HostBinding('style.display') display: string = 'none';
  @HostBinding('class.nested') nested: boolean = false;
  progressOffset: string = '';
  progressWidth: string = '';


  constructor(
    public directive: GanttBarDirective,
    private ganttChart: GanttChartComponent,
  ) {
    effect(() => {

      this.left = directive.left();
      this.width = directive.width();
      this.display = directive.display();

      if (this.ganttChart.nowBar) {
        const start = Math.round(directive.start().getTime()/(60_000));
        const now = Math.round(this.ganttChart.now()!.time.getTime()/(60_000));
        const end = Math.round(directive.end().getTime()/60_000);


        if (start < now && now < end) {
          const offset = this.ganttChart.now()?.offset ?? 0;
          const cursor = offset - (directive.position?.offset ?? 0);

          // couldn't find a better way to make the progress div align perfectly than
          // adding some empirical correction
          this.progressOffset = `${cursor - 2}px`;
          const taskWidth = directive.position?.duration ?? 0;
          this.progressWidth = `${taskWidth - cursor + 3}px`;
        }
      }
    });
    this.nested = directive.nested;
  }
}
