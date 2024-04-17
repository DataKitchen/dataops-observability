import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RunTimeComponent } from './run-time.component';
import { ParseDatePipe } from '@observability-ui/ui';
import { RunAlertType } from '@observability-ui/core';

describe('run-time.component', () => {

  let component: RunTimeComponent;
  let fixture: ComponentFixture<RunTimeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        RunTimeComponent,
      ],
      imports: [
        ParseDatePipe,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RunTimeComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('only actual (time) is defined', () => {
    it('should show actual time', () => {
      fixture.componentRef.setInput('actual', '2023-05-16T19:59:54.949841+00:00');

      expect(component.time()).toEqual('2023-05-16T19:59:54.949841+00:00');
    });
  });

  describe('actual time is not defined and expected is defined', () => {
    it('should show expected time', () => {
      fixture.componentRef.setInput('expected', '2023-05-16T19:59:54.949841+00:00');

      expect(component.time()).toEqual('2023-05-16T19:59:54.949841+00:00');
    });

  });

  describe('alerts contains an alert of type alertType', () => {
    // in this case we assume `expected` is earlier than actual
    // meaning that the run is late

    it('should show actual and set `lateness` flag', () => {
      fixture.componentRef.setInput('actual', '2023-05-16T20:59:54.949841+00:00');
      fixture.componentRef.setInput('expected', '2023-05-16T19:59:54.949841+00:00');
      fixture.componentRef.setInput('alerts', [{type: RunAlertType.LateStart} as any]);
      fixture.componentRef.setInput('alertType', RunAlertType.LateStart);

      expect(component.lateness()).toBeTruthy();
    });
  });

});
