import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RunStatesComponent } from './run-states.component';
import { Run, RunProcessedStatus } from '@observability-ui/core';
import { TranslatePipeMock } from '@observability-ui/translate';

describe('RunStatesComponent', () => {
  let component: RunStatesComponent;
  let fixture: ComponentFixture<RunStatesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        RunStatesComponent,
        TranslatePipeMock,
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RunStatesComponent);
    component = fixture.componentInstance;

    component.run = { run_states: [] } as unknown as Run;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should use the run status when present', () => {
    component.run = { status: RunProcessedStatus.Missing } as unknown as Run;
    component.ngOnChanges({
      run: {
        previousValue: undefined,
        currentValue: component.run,
        firstChange: false
      } as any
    });
    expect(component.state).toBe(RunProcessedStatus.Missing);
  });

  it('should be completed state if the run status is not set', () => {
    component.run = {} as unknown as Run;
    component.ngOnChanges({
      run: {
        previousValue: undefined,
        currentValue: component.run,
        firstChange: false
      } as any
    });
    expect(component.state).toBe(RunProcessedStatus.Completed);
  });
});
