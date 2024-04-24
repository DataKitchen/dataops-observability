import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GanttChartComponent } from './gantt-chart.component';
import { GanttTaskComponent } from './gantt-task.component';
import { GanttBarDirective } from './gantt-bar.directive';
import { GanttLabelDirective } from './gantt-label.directive';

@NgModule({
  imports: [
    CommonModule,
  ],
  declarations: [ GanttChartComponent, GanttTaskComponent, GanttBarDirective, GanttLabelDirective ],
  exports: [ GanttChartComponent, GanttTaskComponent, GanttBarDirective, GanttLabelDirective ]
})
export class GanttChartModule {
}
