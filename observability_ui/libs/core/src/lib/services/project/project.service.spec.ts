import { TestBed } from '@angular/core/testing';
import { ConfigService } from '../../config/config.service';
import { ProjectService } from './project.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

describe('ProjectService', () => {
  let service: ProjectService;
  let httpClient: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule
      ],
      declarations: [],
      providers: [
        ProjectService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    service = TestBed.inject(ProjectService);
    httpClient = TestBed.inject(HttpTestingController);
  });

  it('should create', () => {
    expect(service).toBeDefined();
  });

  it('should get all events', (done) => {
    service.getEvents({
      parentId: 'projectId'
    }).subscribe(() => {
      done();
    });

    httpClient.expectOne('base/observability/v1/projects/projectId/events?sort=&count=0&page=1')
      .flush({});
  });

  it('should get all events', (done) => {
    service.getAllEvents({
      parentId: 'projectId'
    }).subscribe(() => {
      done();
    });

    httpClient.expectOne('base/observability/v1/projects/projectId/events?sort=&count=0&page=1')
      .flush({});
  });

  it('should get a test by id', (done) => {
    service.getTestById('123').subscribe(() => {
      done();
    });

    httpClient.expectOne('base/observability/v1/test-outcomes/123')
      .flush({});
  });

  it('should get a page of tests', (done) => {
    service.getTests({parentId: 'projectId', count: 10}).subscribe(() => {
      done();
    });

    httpClient.expectOne('base/observability/v1/projects/projectId/tests?sort=&count=10&page=1')
      .flush({});
  });

  it('should get all the tests', (done) => {
    service.getAllTests({parentId: 'projectId'}).subscribe(() => {
      done();
    });

    httpClient
      .expectOne('base/observability/v1/projects/projectId/tests?sort=&count=0&page=1')
      .flush({total: 100});

      httpClient
      .expectOne('base/observability/v1/projects/projectId/tests?sort=&count=100&page=1')
      .flush({});
  });

  it('should get a page of alerts', (done) => {
    service.getAlerts({parentId: 'projectId', count: 10}).subscribe(() => {
      done();
    });

    httpClient.expectOne('base/observability/v1/projects/projectId/alerts?sort=&count=10&page=1')
      .flush({});
  });
});
