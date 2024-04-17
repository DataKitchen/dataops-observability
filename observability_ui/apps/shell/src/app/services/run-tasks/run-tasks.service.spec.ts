import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ConfigService } from '@observability-ui/core';
import { RunTasksService } from './run-tasks.service';

describe('run-tasks.service', () => {

  let service: RunTasksService;
  let httpClient: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      providers: [
        RunTasksService,
        MockProvider(ConfigService, class {
          get = () => 'base_url';
        })
      ],
    });

    service = TestBed.inject(RunTasksService);
    httpClient = TestBed.inject(HttpTestingController);

  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

  it('should call endpoint', (done) => {
    service.findAll({ parentId: 'parentId' })
      .subscribe(() => {
        done();
      });

    httpClient.expectOne('base_url/observability/v1/runs/parentId/tasks').flush({});
  });

});
