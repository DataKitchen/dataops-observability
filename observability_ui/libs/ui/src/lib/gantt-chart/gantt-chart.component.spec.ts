import { Component, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { GanttTaskComponent } from './gantt-task.component';
import { GanttBarDirective } from './gantt-bar.directive';
import { GanttChartComponent } from './gantt-chart.component';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';
import { GanttLabelDirective } from './gantt-label.directive';

describe('GanttChartComponent', () => {
  @Component({
    selector: 'test-componet',
    template: `
      <gantt-chart
        [start]="start"
        [end]="end"
        [nowBar]="true">

        <ng-template ganttLabel
          let-taskGroup="group">
          <div>{{ taskGroup.label }}</div>
        </ng-template>

        <ng-template [ganttBar]="task1.id"
          [ganttBarLabel]="task1.label"
          [ganttBarStart]="task1.start"
          [ganttBarEnd]="task1.end"
          [ganttBarGroupBy]="task1.id"
          [ganttBarContext]="task1">
          <gantt-task></gantt-task>
        </ng-template>

        <ng-template [ganttBar]="childTask.id"
          [ganttBarLabel]="childTask.label"
          [ganttBarStart]="childTask.start"
          [ganttBarEnd]="childTask.end"
          [ganttBarGroupBy]="childTask.id"
          [ganttBarParent]="childTask.parent"
          [ganttBarContext]="childTask">
          <gantt-task></gantt-task>
        </ng-template>

        <ng-template [ganttBar]="task2.id"
          [ganttBarLabel]="task2.label"
          [ganttBarStart]="task2.start"
          [ganttBarEnd]="task2.end"
          [ganttBarGroupBy]="task2.id"
          [ganttBarContext]="task2">
          <gantt-task></gantt-task>
        </ng-template>
      </gantt-chart>
    `,
  })
  class TestComponent {
    start = new Date('2023-03-10T00:00:00.000+00:00');
    end = new Date('2023-03-10T23:59:59.999+00:00');

    task1 = {
      id: 'task-1',
      label: 'Task 1',
      start: new Date('2023-03-10T08:00:00.000+00:00'),
      end: new Date('2023-03-10T09:30:00.000+00:00'),
    };
    childTask = {
      id: 'child-task-1',
      parent: 'task-1',
      label: 'Child Task 1',
      start: new Date('2023-03-10T08:00:00.000+00:00'),
      end: new Date('2023-03-10T09:00:00.000+00:00'),
    };
    task2 = {
      id: 'task-2',
      label: 'Task 2',
      start: new Date('2023-03-10T09:30:00.000+00:00'),
      end: new Date('2023-03-10T10:00:00.000+00:00'),
    };

    @ViewChild(GanttChartComponent) chart: GanttChartComponent;
    @ViewChildren(GanttBarDirective) tasks: QueryList<GanttBarDirective>;
  }

  const barsWidth = 1200;

  let fixture: ComponentFixture<TestComponent>;
  let testComponent: TestComponent;

  let testScheduler: TestScheduler;

  beforeEach(async () => {
    testScheduler = new TestScheduler();

    TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        GanttTaskComponent,
        GanttBarDirective,
        GanttLabelDirective,
        GanttChartComponent,
      ],
      providers: [
        {provide: rxjsScheduler, useValue: testScheduler},
      ],
    });

    fixture = TestBed.createComponent(TestComponent);
    testComponent = fixture.componentInstance;

    fixture.detectChanges();
    await fixture.whenStable();

    testComponent.chart['barsContainer'] = {nativeElement: { clientWidth: barsWidth }} as any;
  });

  it('should create', () => {
    expect(testComponent.chart).toBeDefined();
  });

  it('should render the ticks', () => {
    const format = 'hh:mm a';
    const start = testComponent.start;
    const end = testComponent.end;

    expect(testComponent.chart.ticks()).toEqual([ {time: start, format}, {time: expect.any(Date), format}, {time: expect.any(Date), format}, {time: expect.any(Date), format}, {time: end, format} ]);
  });

  it('should render the now bar', () => {
    expect(testComponent.chart.now()).toEqual({offset: expect.any(Number), time: expect.any(Date)});
  });

  it('should not render the now bar when input false', async () => {
    testComponent.chart.nowBar = false;
    testComponent.chart.resizeTasks(); // Trigger the now() signal
    fixture.detectChanges();
    await fixture.whenStable();
    expect(testComponent.chart.now()).toBeNull();
  });

  describe('resizeTasks()', () => {
    it('should recalculate the positioning of tasks', () => {
      testComponent.chart.resizeTasks();
      fixture.detectChanges();

      expect(testComponent.tasks.toArray().map((task) => ({left: task.left(), width: task.width(), display: task.display()})))
        .toEqual([
          {left: expect.stringMatching(/^399\.?([0-9]?)*px$/), width: expect.stringMatching(/^74\.?([0-9]?)*px$/), display: 'inherit'},
          {left: expect.stringMatching(/^399\.?([0-9]?)*px$/), width: expect.stringMatching(/^49\.?([0-9]?)*px$/), display: 'inherit'},
          {left: expect.stringMatching(/^474\.?([0-9]?)*px$/), width: expect.stringMatching(/^24\.?([0-9]?)*px$/), display: 'inherit'},
        ]);
    });
  });
});
