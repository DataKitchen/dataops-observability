import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { InstancesStore } from './instances.store';
import { InstancesService } from '../../services/instances/instances.service';
import { Mocked } from '@datakitchen/ngx-toolkit';
import { of } from 'rxjs';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { InstanceAlert, InstanceAlertType, InstanceStatus, ProjectService, RunProcessedStatus } from '@observability-ui/core';
import { ProjectRunsService } from '../../services/project-runs/project-runs.service';
import { ComponentsService } from '../../services/components/components.service';

describe('instances.store', () => {
  const projectId = '6238a101-74e0-4edb-93c6-994da8fa2c2d';
  const instances = [ { id: 'f05db1f5' } ];
  const runs = [
    {
      'end_time': '2023-02-18T03:52:23',
      'id': 'f05db1f5-3430-4067-a06d-75cbbeafcc65',
      'key': 'def',
      'listening': false,
      'pipeline': { 'display_name': 'aarthy_g', 'id': '362154b4-5653-49dd-8d73-601264da30b7', 'key': 'aarthy_g' },
      'run_states': [],
      'start_time': '2023-02-18T03:52:17',
      'status': 'COMPLETED',
      'tasks_summary': [ { 'count': 0, 'status': 'MISSING' }, {
        'count': 0,
        'status': 'COMPLETED_WITH_WARNINGS'
      }, { 'count': 0, 'status': 'RUNNING' }, { 'count': 0, 'status': 'PENDING' }, {
        'count': 0,
        'status': 'COMPLETED'
      }, { 'count': 0, 'status': 'FAILED' } ]
    },
    {
      'end_time': '2023-02-18T03:09:44',
      'id': '6baf5e8d-fd57-4f76-958e-c718bae30eb4',
      'key': 'abc',
      'listening': false,
      'pipeline': {
        'display_name': 'Aarthy Pipeline E',
        'id': 'a577e35a-d0ae-44b9-b952-1be76a94b849',
        'key': 'aarthy_e'
      },
      'run_states': [] as any[],
      'start_time': '2023-02-18T02:20:24',
      'status': 'COMPLETED',
      'tasks_summary': [ { 'status': 'RUNNING' }, { 'count': 0, 'status': 'MISSING' }, {
        'count': 0,
        'status': 'FAILED'
      }, { 'count': 0, 'status': 'COMPLETED_WITH_WARNINGS' }, { 'count': 0, 'status': 'COMPLETED' }, {
        'count': 0,
        'status': 'PENDING'
      } ]
    },
    {
      'end_time': '2023-02-18T03:10:03',
      'id': 'fcf7de49-1208-4492-921d-fcfa612731f2',
      'key': 'abc',
      'listening': false,
      'pipeline': { 'display_name': 'aarthy_f', 'id': '347f5dda-d620-40f3-ac4e-e6f73ddea4f3', 'key': 'aarthy_f' },
      'run_states': [],
      'start_time': '2023-02-18T03:09:58',
      'status': 'COMPLETED',
      'tasks_summary': [ { 'count': 0, 'status': 'MISSING' }, {
        'count': 0,
        'status': 'COMPLETED_WITH_WARNINGS'
      }, { 'count': 0, 'status': 'RUNNING' }, { 'count': 0, 'status': 'PENDING' }, {
        'count': 0,
        'status': 'COMPLETED'
      }, { 'count': 0, 'status': 'FAILED' } ]
    }
  ];
  const tests = [ { id: 'test-id-1', name: 'test 1' }, { id: 'test-id-2', name: 'test 2' } ];
  const components = [ { id: '1', display_name: 'Component 1' }, { id: '2', display_name: 'Component 2' } ];
  const dagResponse = {
    nodes: [
      {
        'component': {
          'created_by': null as any,
          'created_on': '2022-10-30T13:55:18+00:00',
          'description': null as any,
          'display_name': 'aarthy_f',
          'id': '347f5dda-d620-40f3-ac4e-e6f73ddea4f3',
          'key': 'aarthy_f',
          'labels': null as any,
          'name': null as any,
          'project': '6238a101-74e0-4edb-93c6-994da8fa2c2d',
          'type': 'BATCH_PIPELINE'
        },
        'edges': [ {
          'component': null,
          'id': '6d77758e-9922-40d5-a208-c245f3846da5'
        }, { 'component': 'a577e35a-d0ae-44b9-b952-1be76a94b849', 'id': 'eea0ca02-0b3f-4145-a69d-081bc46a80e4' } ]
      },
      {
        'component': {
          'created_by': null,
          'created_on': '2022-10-30T13:55:18+00:00',
          'description': null,
          'display_name': 'aarthy_g',
          'id': '362154b4-5653-49dd-8d73-601264da30b7',
          'key': 'aarthy_g',
          'labels': null,
          'name': null,
          'project': '6238a101-74e0-4edb-93c6-994da8fa2c2d',
          'type': 'BATCH_PIPELINE'
        },
        'edges': [ {
          'component': null,
          'id': 'b912eccd-17f0-42ff-8293-f8ae888f5e50'
        }, { 'component': '347f5dda-d620-40f3-ac4e-e6f73ddea4f3', 'id': '06e1e591-6ef4-40ad-9514-64296f2d2722' } ]
      },
      {
        'component': {
          'created_by': null,
          'created_on': '2022-10-30T13:55:18+00:00',
          'description': 'This pipeline is used for QA testing.\nThis pipeline is used for QA testing.\nThis pipeline is used for QA testing. This pipeline is used for QA testing.This pipeline is used foThis pipeline is used for QA testing.This pipeline is used for QA testing.This p',
          'display_name': 'Aarthy Pipeline E',
          'id': 'a577e35a-d0ae-44b9-b952-1be76a94b849',
          'key': 'aarthy_e',
          'labels': null,
          'name': 'Aarthy Pipeline E',
          'project': '6238a101-74e0-4edb-93c6-994da8fa2c2d',
          'type': 'BATCH_PIPELINE'
        }, 'edges': [ { 'component': null, 'id': '0c0de92d-322b-40b9-9166-f00ce982a088' } ]
      }
    ]
  };
  const alerts = [
    {
      id: '1',
      run: null,
      level: 'ERROR',
      type: InstanceAlertType.OutOfSequence,
      name: 'Some Alert',
      description: '',
      created_on: null,
      components: [],
    } as InstanceAlert,
  ];

  let store: InstancesStore;
  let service: Mocked<InstancesService>;
  let runService: Mocked<ProjectRunsService>;
  let projectService: Mocked<ProjectService>;
  let testScheduler: TestScheduler;
  let upcomingInstance = { expected_start_time: '11/11/2021' };

  beforeEach(async () => {
    testScheduler = new TestScheduler();

    TestBed.configureTestingModule({
      providers: [
        InstancesStore,
        MockProvider(InstancesService, {
          findAll: jest.fn().mockReturnValue(of({ entities: instances, total: instances.length })),
          getComponents: jest.fn().mockReturnValue(of({ entities: components, total: components.length })),
          getDag: jest.fn().mockReturnValue(of(dagResponse)),
          findUpcomingInstances: jest.fn().mockReturnValue(of({ entities: [ upcomingInstance, ] })),
        }),
        MockProvider(ComponentsService, {
          getSchedules: jest.fn().mockReturnValue(of([]))
        }),
        MockProvider(ProjectRunsService, {
          findAll: jest.fn().mockReturnValue(of({ entities: runs, total: runs.length })),
        }),
        MockProvider(ProjectService, {
          getTestById: jest.fn().mockReturnValue(of(tests[1])),
          getTests: jest.fn().mockReturnValue(of({ entities: tests, total: tests.length })),
          getAllTests: jest.fn().mockReturnValue(of({ entities: [] })),
          getAllEvents: jest.fn().mockReturnValue(of({ entities: [] })),
          getAlerts: jest.fn().mockReturnValue(of({ entities: alerts, total: alerts.length })),
        }),
      ],
    });

    store = TestBed.inject(InstancesStore);
    service = TestBed.inject(InstancesService) as Mocked<InstancesService>;
    runService = TestBed.inject(ProjectRunsService) as Mocked<ProjectRunsService>;
    projectService = TestBed.inject(ProjectService) as Mocked<ProjectService>;
  });

  it('should exists', () => {
    expect(store).toBeTruthy();
  });

  describe('findAllBachRuns()', () => {
    beforeEach(() => {
      store.dispatch('findAllBachRuns', 'projectId', '123');
    });

    it('should get all the runs from the service', () => {
      expect(runService.findAll).toBeCalledWith({ parentId: 'projectId', filters: { instance_id: '123' } });
    });

    it('should update the state with the runs', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({
        runs: {
          list: runs,
          total: runs.length,
          page: undefined,
          count: undefined,
          sort: undefined
        }
      }));
    });
  });

  describe('clearBatchRuns()', () => {
    it('should empty the runs in the state', () => {
      store.dispatch('clearBatchRuns');
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({ runs: { list: [], total: 0 } }));
    });
  });

  describe('findComponents()', () => {
    beforeEach(() => {
      store.dispatch('findComponents', '12');
    });

    it('should get the all components from the service', () => {
      expect(service.getComponents).toBeCalledWith('12');
    });

    it('should update the state with the components', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({ components }));
    });
  });

  describe('getTestsByPage()', () => {
    const request = { filters: { instance_id: '123' }, page: 1, count: 10, sort: 'desc' as any };

    beforeEach(() => {
      store.dispatch('getTestsByPage', projectId, request);
    });

    it('should get the runs from the service', () => {
      expect(projectService.getTests).toBeCalledWith({ ...request, parentId: projectId });
    });

    it('should update the state with the runs and the request', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({
        tests: expect.objectContaining({
          list: tests,
          total: tests.length,
          page: request.page,
          count: request.count,
          sort: 'desc'
        })
      }));
    });
  });

  describe('getAlertsByPage()', () => {
    const request = { page: 1, count: 10, sort: 'desc' as any };

    beforeEach(() => {
      store.dispatch('getAlertsByPage', projectId, '123', request);
    });

    it('should get the alerts from the service', () => {
      expect(projectService.getAlerts).toBeCalledWith({
        ...request,
        filters: { instance_id: '123' },
        parentId: projectId
      });
    });

    it('should update the state with the alerts', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({
        instanceAlerts: expect.objectContaining({
          list: alerts,
          total: alerts.length,
          page: request.page,
          count: request.count,
          sort: 'desc'
        })
      }));
    });
  });

  describe('getOutOfSequenceAlert()', () => {
    const projectId = '15';
    const instanceId = 'f05db1f5';

    beforeEach(() => {
      store.dispatch('getOutOfSequenceAlert', projectId, instanceId);
    });

    it('should get one out of sequence alert for the instance', () => {
      expect(projectService.getAlerts).toBeCalledWith({
        parentId: projectId,
        filters: { instance_id: instanceId, type: InstanceAlertType.OutOfSequence },
        count: 1
      });
    });

    it('should set the state with the out of sequence alert', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({
        alerts: expect.objectContaining({ outOfSequence: alerts[0] }),
      }));
    });
  });

  describe('getDayInstances()', () => {
    const request = { parentId: '123' };
    const reportDate = new Date();
    const dateRangeStart = new Date(reportDate.setHours(0, 0, 0, 0)).toISOString();
    const dateRangeEnd = new Date(reportDate.setHours(23, 59, 59, 999)).toISOString();

    beforeEach(() => {
      store.dispatch('getDayInstances', request, reportDate);
    });

    it('should get the instances by end time range', () => {
      expect(service.findAll).toBeCalledWith({
        ...request,
        filters: { end_range_begin: dateRangeStart, end_range_end: dateRangeEnd }
      });
    });

    it('should get the active instances', () => {
      expect(service.findAll).toBeCalledWith({
        ...request,
        filters: {
          active: true,
          start_range_end: dateRangeEnd,
        }
      });
    });

    it('should populate todayInstances prop in the state', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({ todayInstances: [ ...instances, ...instances, upcomingInstance ] }));
    });
  });

  describe('getDayInstanceRuns()', () => {
    const projectId = '15';
    const instanceId = 'f05db1f5';
    const reportDate = new Date();
    const dateRangeStart = new Date(reportDate.setHours(0, 0, 0, 0)).toISOString();
    const dateRangeEnd = new Date(reportDate.setHours(23, 59, 59, 999)).toISOString();

    beforeEach(() => {
      store.dispatch('getDayInstanceRuns', projectId, [ instanceId ], reportDate);
    });

    it('should get the instance runs by end time range', () => {
      expect(runService.findAll).toBeCalledWith({
        parentId: projectId,
        filters: { instance_id: [ instanceId ], end_range_begin: dateRangeStart, end_range_end: dateRangeEnd }
      });
    });

    it('should get the running runs', () => {
      expect(runService.findAll).toBeCalledWith({
        parentId: projectId,
        filters: { instance_id: [ instanceId ], status: [ RunProcessedStatus.Running ] }
      });
    });

    it('should populate the runs in the state', () => {
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({
        runs: {
          page: 0,
          list: [ ...runs, ...runs ],
          total: runs.length * 2,
          count: runs.length * 2
        }
      }));
    });
  });

  describe('findAllWithUpcoming', () => {
    it('should get instances and upcoming instances', () => {
      // when status is not unset
      testScheduler.run(({ expectObservable }) => {
        expectObservable(store.findAllWithUpcoming({ filters: {} })).toBe('(a|)', { a: [ ...instances, upcomingInstance ] });
      });

      // when status is set and contains 'UPCOMING'
      testScheduler.run(({ expectObservable }) => {
        expectObservable(store.findAllWithUpcoming({
          filters: {
            status: [ InstanceStatus.Upcoming, InstanceStatus.Completed ],
          }
        })).toBe('(a|)', { a: [ ...instances, upcomingInstance ] });
      });
    });

    it('should only get instances but not upcoming instances', () => {
      // when status is set and it does not contain 'UPCOMING'
      testScheduler.run(({ expectObservable }) => {
        expectObservable(store.findAllWithUpcoming({
          filters: {
            status: [ InstanceStatus.Completed, InstanceStatus.Warning ]
          }
        })).toBe('(a|)', { a: instances });
      });

    });

    it('should not get instances but only upcoming instances', () => {
      // when status is set and it does not contain any of the other statuses
      testScheduler.run(({ expectObservable }) => {
        expectObservable(store.findAllWithUpcoming({
          filters: {
            status: [ InstanceStatus.Upcoming ]
          }
        })).toBe('(a|)', { a: [ upcomingInstance ] });
      });

    });

  });
});
