import {ComponentFixture, TestBed} from '@angular/core/testing';
import {RunDetailsComponent} from './run-details.component';
import {MockComponent, MockComponents, MockDirective, MockPipe} from 'ng-mocks';
import {RunEventsComponent} from '../run-events/run-events.component';
import {ActivatedRoute, Params} from '@angular/router';
import {BehaviorSubject, of} from 'rxjs';
import {Run} from '@observability-ui/core';
import {TranslatePipeMock} from '@observability-ui/translate';
import {RouterTestingModule} from '@angular/router/testing';
import {MatLegacyTabLink as MatTabLink, MatLegacyTabNav as MatTabNav, MatLegacyTabNavPanel as MatTabNavPanel} from '@angular/material/legacy-tabs';
import {DetailsHeaderComponent, DurationComponent, DurationPipe} from '@observability-ui/ui';
import {RunsStore} from '../../../stores/runs/runs.store';
import {RunStatesComponent} from '../runs-table/run-states/run-states.component';
import {TaskTestSummaryComponent} from '../../task-test-summary/task-test-summary.component';
import { RunTimeComponent } from '../runs-table/run-time/run-time.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('RunDetailsComponent', () => {
  const start_time = '2022-08-09T15:29:20.381879';
  const end_time = '2022-08-09T15:29:20.381879';
  const runId = "f4dd48b3-a6da-497a-be1a-c9dd8e9d1efc";

  let paramsSubject: BehaviorSubject<Params>;
  let runSubject$: BehaviorSubject<Run>;

  let component: RunDetailsComponent;
  let fixture: ComponentFixture<RunDetailsComponent>;

  beforeEach(async () => {
    paramsSubject = new BehaviorSubject<Params>({ id: runId });
    runSubject$ = new BehaviorSubject<Run>({
      runId,
      start_time,
      end_time,
      pipeline: { name : 'My Pipeline' },
    } as unknown as Run);

    await TestBed.configureTestingModule({
      declarations: [
        RunDetailsComponent,
        TranslatePipeMock,
        MockComponent(RunEventsComponent),
        MockPipe(DurationPipe),
        MockComponents(MatTabNavPanel, MatTabNav),
        MockDirective(MatTabLink),
        MockComponent(DetailsHeaderComponent),
        MockComponent(DurationComponent),
        MockComponent(RunStatesComponent),
        MockComponent(RunTimeComponent)
      ],
      imports: [
        RouterTestingModule,
        TaskTestSummaryComponent,
      ],
      providers: [
        MockProvider(RunsStore, class {
          list$ = of([{ id: runId }] as any[]);
          selected$= runSubject$.asObservable();
        }),
        MockProvider(ActivatedRoute, class {
          params = paramsSubject;
          snapshot = {
            params: { id: runId } as Params,
          };
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(RunDetailsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('alignInkBar()', () => {
    it('should align the tabs ink bar', () => {
      component.tabs = { _alignInkBarToSelectedTab: jest.fn() } as any;
      component.alignInkBar();
      expect(component.tabs._alignInkBarToSelectedTab).toBeCalled();
    });
  });
});
