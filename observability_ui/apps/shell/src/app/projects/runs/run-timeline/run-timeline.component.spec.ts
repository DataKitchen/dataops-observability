import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RunTimelineComponent } from './run-timeline.component';
import { ActivatedRoute, Router } from '@angular/router';
import { ActivatedRouteMock, Mocked } from '@datakitchen/ngx-toolkit';
import { RunTasksStore } from '../../../stores/run-tasks/run-tasks.store';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { of } from 'rxjs';
import { MockComponent } from 'ng-mocks';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { RunsStore } from '../../../stores/runs/runs.store';
import { GanttChartModule } from '@observability-ui/ui';

describe('run-timeline.component', () => {
  const runId = '123';

  let store: Mocked<RunTasksStore>;
  let runsStore: Mocked<RunsStore>;

  let component: RunTimelineComponent;
  let fixture: ComponentFixture<RunTimelineComponent>;

  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatCardModule,
        GanttChartModule,
      ],
      declarations: [
        RunTimelineComponent,
        MockComponent(MatProgressSpinner),
      ],
      providers: [
        MockProvider(RunTasksStore, class {
          list$ = of([]);
        }),
        MockProvider(RunsStore, class {
          getOne = () => of({ id: runId });
        }),
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {}, ActivatedRouteMock({
            runId: runId,
          })),
        }
      ]
    }).compileComponents();

    store = TestBed.inject(RunTasksStore) as Mocked<RunTasksStore>;
    runsStore = TestBed.inject(RunsStore) as Mocked<RunsStore>;

    fixture = TestBed.createComponent(RunTimelineComponent);
    component = fixture.componentInstance;

    router = TestBed.inject(Router);
    router.navigate = jest.fn();

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should fetch tasks for timeline', () => {
    expect(store.dispatch).toBeCalledWith('findAll', { parentId: runId });
  });

  it('should refresh header details', () => {
    expect(runsStore.dispatch).toBeCalledWith('getOne', runId);
  });
});
