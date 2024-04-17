import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { RunEventsComponent } from './run-events.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MockComponent } from 'ng-mocks';
import { FilterFieldComponent, FilterFieldOptionComponent } from '@observability-ui/ui';
import { ConfigService, ProjectStore, RunTask } from '@observability-ui/core';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { RunTasksStore } from '../../../stores/run-tasks/run-tasks.store';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { ActivatedRoute } from '@angular/router';
import { TranslatePipeMock } from '@observability-ui/translate';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { EventsTableComponent } from '../events-table/events-table.component';
import { ReactiveFormsModule } from '@angular/forms';
import { RunsStore } from '../../../stores/runs/runs.store';

describe('RunEventsComponent', () => {
  const runId = '1';
  const tasks = [ {task: {key: 'A', display_name: 'A'}}, {task: {key: 'B', display_name: 'B'}}, {task: {key: 'C', display_name: 'C'}} ] as RunTask[];

  let store: Mocked<ProjectStore>;
  let runTasksStore: Mocked<RunTasksStore>;
  let runsStore: Mocked<RunsStore>;

  let component: RunEventsComponent;
  let fixture: ComponentFixture<RunEventsComponent>;

  beforeEach(async () => {

    await TestBed.configureTestingModule({
      declarations: [
        RunEventsComponent,
        MockComponent(EventsTableComponent),
        MockComponent(FilterFieldComponent),
        MockComponent(FilterFieldOptionComponent),
        TranslatePipeMock,
      ],
      imports: [
        HttpClientTestingModule,
        ReactiveFormsModule,
      ],
      providers: [
        MockProvider(RunTasksStore, class {
          list$ = of(tasks);
        }),
        MockProvider(RunsStore, class {
        }),
        MockProvider(ProjectStore, class {
          list$ = of([]);
          total$ = of(0);
          current$ = of({id: '1'});
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        }),
        MockProvider(ParameterService),
        MockProvider(StorageService),
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {}, ActivatedRouteMock({
            projectId: '1',
            runId: runId,
          })),
        },
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    }).compileComponents();

    store = TestBed.inject(ProjectStore) as Mocked<ProjectStore>;
    runTasksStore = TestBed.inject(RunTasksStore) as Mocked<RunTasksStore>;
    runsStore = TestBed.inject(RunsStore) as Mocked<RunsStore>;

    fixture = TestBed.createComponent(RunEventsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should set a filters storage key', () => {
    expect(component.storageKey).toBe('1:RunEvents:1');
  });

  it('should get all tasks for the run', () => {
    expect(runTasksStore.dispatch).toBeCalledWith('findAll', {parentId: runId});
  });


  describe('onTableChange()', () => {
    it('should pass the filters to the store', () => {
      component.onTableChange({pageIndex: 0, pageSize: 10, search: { event_type: 'A,B', task_id: '1,2'}});
      expect(store.dispatch).toBeCalledWith('getEventsByPage', expect.objectContaining({
        parentId: '1',
        sort: 'desc',
        page: 0,
        count: 10,
        filters: {
          run_id: runId,
          task_id: [ '1', '2' ],
          event_type: [ 'A', 'B' ],
        },
      }));
    });

    it('should refresh header details', () => {
      component.onTableChange({pageIndex: 0, pageSize: 10, search: { event_type: 'A,B', task_id: '1,2'}});
      expect(runsStore.dispatch).toBeCalledWith('getOne', runId);
    });
  });
});
