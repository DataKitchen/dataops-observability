import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProjectOverviewComponent } from './overview.component';
import { parseDate, ProjectStore, Run, RunProcessedStatus, Instance } from '@observability-ui/core';
import { ParameterService, rxjsScheduler } from '@datakitchen/ngx-toolkit';
import { of } from 'rxjs';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { MockComponent, MockDirective, MockModule } from 'ng-mocks';
import { DkTooltipDirective, DotComponent, DotTemplateDirective, DotsChartComponent, FilterFieldModule, GanttBarDirective, GanttChartComponent, GanttLabelDirective, GanttTaskComponent } from '@observability-ui/ui';
import { ActivatedRoute, Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { TranslatePipeMock } from '@observability-ui/translate';
import { InstancesStore } from '../../stores/instances/instances.store';
import { MatIcon } from '@angular/material/icon';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { JourneysStore } from '../journeys/journeys.store';

describe('ProjectOverviewComponent', () => {
  const projectId = '1';
  const instances = [
    {
      'active': true,
      'alerts_summary': [
        {
          'description': 'Batch pipeline \'aarthy_qa\' run status changed from end state',
          'level': 'WARNING',
          'count': 2,
        },
        {
          'description': 'Batch pipeline \'aarthy_qa\' run encountered a failure',
          'level': 'ERROR',
          'count': 1,
        },
        {
          'description': 'Batch pipeline \'aarthy_qa\' run completed with warnings',
          'level': 'WARNING',
          'count': 1,
        },
        {
          'description': 'Batch pipeline \'aarthy_qa\' run encountered a failure',
          'level': 'ERROR',
          'count': 1,
        }
      ],
      'id': '71321dc6-b626-43d0-875b-4aa273f59b15',
      'journey': {
        'id': '068fecf3-8ed6-4860-8be5-e7945caafc60',
        'name': 'Aarthy Test'
      },
      'runs_summary': [
        {
          'count': 1,
          'status': 'COMPLETED_WITH_WARNINGS'
        },
        {
          'count': 3,
          'status': 'FAILED'
        }
      ],
      'start_time': '2023-03-01T16:05:20.170319+00:00',
      'end_time': null,
    } as unknown,
  ] as Instance[];
  const runs = [
    {
      start_time: '2020-01-01T00:00:00',
      end_time: '2020-01-01T00:10:00',
      status: RunProcessedStatus.Running,
      pipeline: {
        name: 'Pipeline A',
      },
    },
    {
      start_time: '2020-01-01T00:10:05',
      end_time: null,
      status: RunProcessedStatus.Running,
      pipeline: {
        name: 'Pipeline A',
      },
    },
    {
      start_time: null,
      end_time: null,
      listening: false,
      status: RunProcessedStatus.Pending,
      pipeline: {
        name: 'Pipeline B',
      },
    },
  ] as Run[];

  let component: ProjectOverviewComponent;
  let fixture: ComponentFixture<ProjectOverviewComponent>;

  let store: Mocked<InstancesStore>;
  let journeysStore: Mocked<JourneysStore>;
  let router: Router;

  let testScheduler: TestScheduler;

  beforeEach(async () => {
    testScheduler = new TestScheduler();

    await TestBed.configureTestingModule({
      declarations: [
        ProjectOverviewComponent,
        MockComponent(GanttChartComponent),
        MockComponent(GanttTaskComponent),
        MockComponent(MatIcon),
        MockComponent(DotComponent),
        MockComponent(DotsChartComponent),
        MockDirective(GanttLabelDirective),
        MockDirective(GanttBarDirective),
        MockDirective(DkTooltipDirective),
        MockDirective(DotTemplateDirective),
        TranslatePipeMock,
      ],
      providers: [
        MockProvider(InstancesStore, class {
          todayInstances$ = of(instances);
          runs$ = of(runs);
          dispatch = jest.fn();
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        }),
        MockProvider(ParameterService, class {
        }),
        MockProvider(ProjectStore, class {
          list$ = of({ id: projectId });
          current$ = of({ id: projectId });
          projectChanged$ = of(false);
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        }),
        MockProvider(JourneysStore, class {
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        }),
        MockProvider(ActivatedRoute),
        {
          provide: rxjsScheduler,
          useValue: testScheduler,
        },
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({
            projectId: 'projectId'
          })
        }
      ],
      imports: [ RouterTestingModule, MockModule(FilterFieldModule) ]
    }).compileComponents();

    store = TestBed.inject(InstancesStore) as Mocked<InstancesStore>;
    journeysStore = TestBed.inject(JourneysStore) as Mocked<JourneysStore>;
    router = TestBed.inject(Router);

    router.navigate = jest.fn();

    fixture = TestBed.createComponent(ProjectOverviewComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  xit('should get all instance journeys', async () => {

    expect(journeysStore.dispatch).toBeCalledWith('findAll', { parentId: projectId });

  });


  describe('parsing instances', () => {
    it('should parse the start and end dates', () => {
      component.instances$.subscribe((todayInstances) => {
        expect(todayInstances).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ start_time: new Date(instances[0].start_time), end_time: expect.any(Date) })
          ])
        );
      });
    });

    it('should pick the most important status from the runs summary', () => {
      component.instances$.subscribe((todayInstances) => {
        expect(todayInstances).toEqual(expect.arrayContaining([ expect.objectContaining({ status: RunProcessedStatus.Failed }) ]));
      });
    });

    it('should count the number of runs', () => {
      component.instances$.subscribe((todayInstances) => {
        expect(todayInstances).toEqual(expect.arrayContaining([ expect.objectContaining({ runsCount: 4 }) ]));
      });
    });

    it('should count the error alerts', () => {
      component.instances$.subscribe((todayInstances) => {
        expect(todayInstances).toEqual(expect.arrayContaining([ expect.objectContaining({ errorAlertsCount: 2 }) ]));
      });
    });

    it('should count the warning alerts', () => {
      component.instances$.subscribe((todayInstances) => {
        expect(todayInstances).toEqual(expect.arrayContaining([ expect.objectContaining({ warningAlertsCount: 3 }) ]));
      });
    });
  });

  describe('parsing runs', () => {
    it('should parse the start and end dates', () => {
      component.instanceRuns$.subscribe((runs) => {
        expect(runs).toEqual(
          expect.arrayContaining([
            expect.objectContaining({
              start_time: parseDate(runs[0].start_time as any),
              end_time: parseDate(runs[0].end_time as any)
            })
          ])
        );
      });
    });

    it('should set default the start and end dates to the instance start and end', () => {
      const start = new Date(instances[0].start_time);
      const end = new Date();
      component.expandedDate = {
        id: 'asd',
        instances: [ { ...instances[0], start_time: start, end_time: end } ]
      } as any;
      component.instanceRuns$.subscribe((runs) => {
        expect(runs).toEqual([ expect.anything(), expect.anything(), expect.objectContaining({
          start_time: start,
          end_time: end
        }) ]);
      });
    });

    it('should set `hasTime` property for Missing and Pending runs', () => {
      const start = new Date(instances[0].start_time);
      const end = new Date();
      component.expandedDate = {
        id: 'asd',
        instances: [ { ...instances[0], start_time: start, end_time: end } ]
      } as any;
      component.instanceRuns$.subscribe((runs) => {
        expect(runs).toEqual([ expect.anything(), expect.anything(), expect.objectContaining({ hasTime: false }) ]);
      });
    });
  });

  describe('expandInstance()', () => {
    const selectedDate = new Date().toISOString();
    const expansionId = '2';
    const expandedTasks = [ { context: instances[0] } ] as any;

    beforeEach(() => {
      component.form.patchValue({ day: selectedDate });
      component.expandDate(expansionId, expandedTasks);
    });

    it('should clear the runs', () => {
      expect(store.dispatch).toBeCalledWith('clearBatchRuns');
    });

    it('should set the expanded instance', () => {
      expect(component.expandedDate).toEqual({ id: expansionId, instances });
    });

    xit('should get the instances for the day', () => {
      expect(store.dispatch).toBeCalledWith('getDayInstanceRuns', projectId, instances.map(i => i.id), new Date(selectedDate));
    });
  });

  describe('collapseInstance()', () => {
    beforeEach(() => {
      component.expandedDate = {} as any;
      component.collapseDate();
    });

    it('should set the expanded instance to null', () => {
      expect(component.expandedDate).toBeNull();
    });

    it('should clear the runs', () => {
      expect(store.dispatch).toBeCalledWith('clearBatchRuns');
    });
  });

  describe('instanceDotsTrackBy()', () => {
    it('should return a unique string for the instance', () => {
      const start = new Date('2023-03-09T10:46:14.097997+00:00');
      const end = new Date('2023-03-09T12:46:14.097997+00:00');

      expect(component.instanceDotsTrackBy(0, {
        id: '1',
        journey: { name: 'Test Journey' },
        status: RunProcessedStatus.Completed,
        start_time: start,
        end_time: end
      } as any))
        .toEqual(`1-Test Journey-COMPLETED-${start}-${end}`);
    });
  });

  describe('instanceGanttTrackBy()', () => {
    it('should return a unique string for the instance', () => {
      const start = new Date('2023-03-09T10:46:14.097997+00:00');
      const end = new Date('2023-03-09T12:46:14.097997+00:00');

      expect(component.instanceGanttTrackBy(0, {
        value: {
          id: '1',
          journey: { name: 'Test Journey' },
          status: RunProcessedStatus.Completed,
          start_time: start,
          end_time: end
        } as any
      }))
        .toEqual(`1-Test Journey-COMPLETED-${start}-${end}`);
    });
  });

  describe('runTrackBy()', () => {
    it('should return a unique string for the run', () => {
      const start = new Date('2023-03-09T10:46:14.097997+00:00');
      const end = new Date('2023-03-09T12:46:14.097997+00:00');

      expect(component.runTrackBy(0, {
        id: '1',
        pipeline: { display_name: 'Test Pipeline' },
        status: RunProcessedStatus.CompletedWithWarnings,
        start_time: start,
        end_time: end
      } as any))
        .toEqual(`1-Test Pipeline-COMPLETED_WITH_WARNINGS-${start}-${end}`);
    });
  });

  describe('today()', () => {
    it('should set the day to today\'s date', () => {
      const expectedDate = new Date().toISOString().slice(0, 10);
      component.form.patchValue({ day: '2023-03-09T00:00:00.000Z' });
      component.today();
      expect(component.form.value).toEqual({ day: expect.stringContaining(expectedDate), journey: null });
    });

  });

  describe('previousDate()', () => {
    it('should change the day to one day before', () => {
      component.form.patchValue({ day: '2023-03-09T00:00:00.000Z' });
      component.previousDate();
      expect(component.form.value).toEqual({ day: '2023-03-08T00:00:00.000Z', journey: null });
    });

    it('should change the day to yesterday if the form has no value', () => {
      const expectedDate = new Date(new Date().getTime() - 1 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
      component.form.patchValue({ day: undefined });
      component.previousDate();
      expect(component.form.value).toEqual({ day: expect.stringContaining(expectedDate), journey: null });
    });
  });

  describe('nextDate()', () => {
    it('should change the day to one day after', () => {
      component.form.patchValue({ day: '2023-03-08T00:00:00.000Z' });
      component.nextDate();
      expect(component.form.value).toEqual({ day: '2023-03-09T00:00:00.000Z', journey: null });
    });

  });
});
