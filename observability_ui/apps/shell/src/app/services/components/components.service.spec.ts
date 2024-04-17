import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { BaseComponent, ComponentType, ConfigService, EntityListResponse, nonReadonlyFields, Schedule } from '@observability-ui/core';
import { ComponentsService } from './components.service';
import { omit } from '@datakitchen/ngx-toolkit';

describe('Pipeline Service', () => {
  let service: ComponentsService;
  let httpClient: HttpTestingController;

  const response = {
    entities: [
      {
        id: '1',
        schedule: '0 1 */2 * *',
        timezone: 'America/New_York',
        expectation: 'BATCH_PIPELINE_START_TIME'
      } as Schedule,
      {
        id: '3',
        schedule: '0 */2 * * *',
        timezone: 'America/New_York',
        expectation: 'BATCH_PIPELINE_END_TIME'
      } as Schedule,
    ],
    total: 2,
  } as EntityListResponse<Schedule>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        ComponentsService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    service = TestBed.inject(ComponentsService);
    httpClient = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('create()', () => {
    it('should create the pipeline', () => {
      const projectId = '15';
      const expected: nonReadonlyFields<BaseComponent> = {
        key: 'p-key',
        name: 'Name',
        description: 'Description',
        type: ComponentType.BatchPipeline,
      };

      service.create(expected, projectId).subscribe();

      httpClient.expectOne({
        method: 'POST',
        url: `base/observability/v1/projects/${projectId}/batch-pipelines`,
      }).flush(expected);
    });
  });

  describe('#update', () => {
    it('should call correct url', () => {

      const projectId = '15';
      const expected = {
        id: 'component_id',
        key: 'p-key',
        name: 'Name',
        description: 'Description',
        type: ComponentType.BatchPipeline,
      } as BaseComponent;

      service.update(expected, projectId).subscribe();

      httpClient.expectOne({
        method: 'PATCH',
        url: `base/observability/v1/projects/${projectId}/batch-pipelines/component_id`,
      }).flush(expected);


    });
  });

  describe('#delete', () => {

    it('should call endpoint', () => {

      service.delete('component_id').subscribe();

      httpClient.expectOne({
        method: 'DELETE',
        url: `base/observability/v1/components/component_id`,
      }).flush({});


    });
  });

  describe('getScheduleExpectations()', () => {
    it('should fetch the expectations for the pipeline', (done) => {
      service.getSchedules('abc').subscribe((resp) => {
        expect(resp).toEqual(response);
        done();
      });

      httpClient.expectOne({
        method: 'GET',
        url: 'base/observability/v1/components/abc/schedules',
      }).flush(response);
    });
  });

  describe('createScheduleExpectation()', () => {
    it('should create a new schedule expectation', (done) => {
      const newSchedule = omit(response.entities[1], [ 'id' ]);
      service.createSchedule('abc', newSchedule).subscribe((resp) => {
        expect(resp).toBe(newSchedule);
        done();
      });

      httpClient.expectOne({
        method: 'POST',
        url: 'base/observability/v1/components/abc/schedules',
      }).flush(newSchedule);
    });
  });

  describe('deleteScheduleExpectation()', () => {
    it('should delete the expectation by id', (done) => {
      const scheduleId = response.entities[0].id;
      service.deleteSchedule(scheduleId).subscribe(() => done());
      httpClient.expectOne({
        method: 'DELETE',
        url: `base/observability/v1/schedules/${scheduleId}`,
      }).flush(null);
    });
  });
});
