import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { TestgenIntegrationComponent } from './testgen-integration.component';
import { InstancesStore } from '../../stores/instances/instances.store';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { of } from 'rxjs';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { TestgenTestType, testTypeHelpLink } from './testgen-integration.model';
import { ProjectService, ProjectStore } from '@observability-ui/core';
import { MockModule } from 'ng-mocks';
import { NgChartsModule } from 'ng2-charts';
import { MatIconModule } from '@angular/material/icon';
import { TranslationModule } from '@observability-ui/translate';

describe('TestgenIntegrationComponent', () => {
  const projectId = '6238a101-74e0-4edb-93c6-994da8fa2c2d';
  const instanceID = '6dd9b5d7-1250-4f37-8545-9777d90c02ac';
  const testId = 'eee72aa0-72fa-4882-95f3-9865506f2c2a';

  const tests = [
    {
      'component': {
        'display_name': 'Validate_Override_In_OBS_RecipeName.Parent_Recipe.parent_variation.Parent',
        'id': 'ff23f600-2184-4172-8638-c6d67c32c73b',
        'tool': null as any,
        'type': 'BATCH_PIPELINE'
      },
      'integrations': [
        {
          'integration_name': 'TESTGEN',
          'table': 'companies',
          'columns': [ 'user_emails', 'address' ],
          'test_suite': 'Source Data Checks',
          'version': 1,
          'test_parameters': [
            { 'name': 'baseline_x', 'value': 700 },
            { 'name': 'baseline_y', 'value': 750 },
            { 'name': 'count', 'value': 5 },
            { 'name': 'threshold', 'value': 500 }
          ]
        }
      ],
      'description': 'True equal-to True',
      'dimensions': [
        'accuracy',
        'completeness',
        'consistency',
        'timeliness',
        'uniqueness',
        'validity'
      ],
      'end_time': '2023-07-12T14:04:34.157513+00:00',
      'external_url': 'https://test.domain.com/#/orders/im/Validate_Override_In_OBS_RecipeName/runs/7938c318-20bc-11ee-b6a7-26f48483abb0',
      'id': 'eee72aa0-72fa-4882-95f3-9865506f2c2a',
      'instance_set': 'be425cc7-d79e-4d89-8c73-3723b754dac2',
      'key': 'my-test-key',
      'max_threshold': 1000,
      'metric_value': 850,
      'metric_name': 'unique_values',
      'min_threshold': 600,
      'name': 'Email is correctly formatted',
      'result': 'Invalid emails: 20, Threshold: 0',
      'run': 'f4637ca5-a1fe-454e-a2cf-54c163f3d054',
      'start_time': '2023-07-12T14:04:34.157513+00:00',
      'status': 'WARNING',
      'task': '0ae92aed-46ca-4797-8e0d-e4dcc5fe3d08',
      'type': 'required'
    }
  ];

  let fixture: ComponentFixture<TestgenIntegrationComponent>;
  let component: TestgenIntegrationComponent;

  let projectService: Mocked<ProjectService>;
  let projectStore: Mocked<ProjectStore>;

  const timezoneMock = function(zone: string) {
    const DateTimeFormat = Intl.DateTimeFormat;
    jest
      .spyOn(global.Intl, 'DateTimeFormat')
      .mockImplementation((locale, options) => new DateTimeFormat(locale, { ...options, timeZone: zone }));
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        MockModule(NgChartsModule),
        MockModule(MatIconModule),
        TestgenIntegrationComponent,
        MockModule(TranslationModule),
      ],
      providers: [
        MockProvider(InstancesStore, class {
          tests$ = of(tests);
          selectedTest$ = of(tests[0]);
          dispatch = jest.fn();
        } as any),
        MockProvider(ProjectStore, class {
          selectTest = jest.fn().mockReturnValue(of(tests[1]));
          selectedTest$ = of(tests[0]);
        }),
        MockProvider(ProjectService, class {
          getTests = jest.fn().mockReturnValue(of({ entities: tests, total: tests.length }));
          getTestById = jest.fn().mockReturnValue(of(tests[0]));
        } as any),
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {}, ActivatedRouteMock({
            id: instanceID,
            testId
          }, {}, ActivatedRouteMock({ projectId }))),
        }
      ]
    });

    fixture = TestBed.createComponent(TestgenIntegrationComponent);
    component = fixture.componentInstance;

    projectStore = TestBed.inject(ProjectStore) as Mocked<ProjectStore>;
    projectService = TestBed.inject(ProjectService) as Mocked<ProjectService>;

    timezoneMock('America/New_York');
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get the test from the store', () => {
    expect(projectStore.dispatch).toBeCalledWith('selectTest', testId);
  });

  it('should get test item', () => {
    expect(component.test()).toEqual(tests[0]);
  });

  it('should get the help link for the test\'s type', () => {
    expect(component.testLink()).toEqual(testTypeHelpLink[tests[0].type as TestgenTestType]);
  });

  it('should get the test history', () => {
    component.test();
    fixture.detectChanges();

    component.chart();
    expect(projectService.getTests).toBeCalledWith({
      parentId: projectId,
      filters: { key: tests[0].key },
      sort: 'desc',
      sort_by: 'start_time',
      count: 20
    });
  });

  describe('for the chart', () => {
    it('should display a max threshold line', () => {
      component.test();
      fixture.detectChanges();

      const chart = component.chart();

      expect(chart).toEqual(expect.objectContaining({
        data: expect.objectContaining({
          datasets: expect.arrayContaining([ expect.objectContaining({
            label: 'Maximum',
            data: [ { x: 0, y: tests[0].max_threshold } ]
          }) ])
        })
      }));
    });

    it('should display a min threshold line', () => {
      component.test();
      fixture.detectChanges();

      const chart = component.chart();

      expect(chart).toEqual(expect.objectContaining({
        data: expect.objectContaining({
          datasets: expect.arrayContaining([ expect.objectContaining({
            label: 'Minimum',
            data: [ { x: 0, y: tests[0].min_threshold } ]
          }) ])
        })
      }));
    });

    it('should render a dataset for the metric_values', () => {
      component.test();
      fixture.detectChanges();

      const chart = component.chart();

      expect(chart).toEqual(expect.objectContaining({
        data: expect.objectContaining({
          datasets: expect.arrayContaining([ expect.objectContaining({
            label: tests[0].name,
            data: [ { x: 0, y: tests[0].metric_value, status: tests[0].status } ]
          }) ])
        })
      }));
    });
  });
});
