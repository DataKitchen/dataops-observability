import { signal, WritableSignal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { GanttTaskComponent } from './gantt-task.component';
import { GanttBarDirective } from './gantt-bar.directive';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { GanttChartComponent } from '../gantt-chart/gantt-chart.component';

describe('GanttTaskComponent', () => {
  let fixture: ComponentFixture<GanttTaskComponent>;
  let component: GanttTaskComponent;

  let leftSignal: WritableSignal<string>;
  let widthSignal: WritableSignal<string>;
  let displaySignal: WritableSignal<string>;
  let startSignal: WritableSignal<Date>;
  let endSignal: WritableSignal<Date>;

  beforeEach(async () => {
    leftSignal = signal('0px');
    widthSignal = signal('0px');
    displaySignal = signal('none');
    startSignal = signal(new Date('11/11/11 12:00'));
    endSignal = signal(new Date('11/11/11 15:00'));

    TestBed.configureTestingModule({
      declarations: [
        GanttTaskComponent,
      ],
      providers: [
        MockProvider(GanttBarDirective),
        MockProvider(GanttChartComponent, class {
          nowBar = true;
          now = signal({
            time: new Date('11/11/11 13:00'),
            offset: 100,
          });
        })
      ]
    });

    fixture = TestBed.createComponent(GanttTaskComponent);
    component = fixture.componentInstance;

    component.directive.left = leftSignal;
    component.directive.width = widthSignal;
    component.directive.display = displaySignal;
    component.directive.start = startSignal;
    component.directive.end = endSignal;

    component.directive.position = {
      offset: 50,
      duration: 150,
    };

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });

  it('should start with default values', () => {
    expect(component.left).toBe('0px');
    expect(component.width).toBe('0px');
    expect(component.display).toBe('none');
  });

  it('should update the left when the directive signal changes', () => {
    leftSignal.set('100px');
    fixture.detectChanges();
    expect(component.left).toBe('100px');
  });

  it('should update the width when the directive signal changes', () => {
    widthSignal.set('50px');
    fixture.detectChanges();
    expect(component.width).toBe('50px');
  });

  it('should update the display when the directive signal changes', () => {
    displaySignal.set('block');
    fixture.detectChanges();
    expect(component.display).toBe('block');
  });

  it('should set running a linear gradient background to show a task progress', () => {
    expect(component.progressOffset).toEqual('48px');
    expect(component.progressWidth).toEqual('103px');

  });
});
