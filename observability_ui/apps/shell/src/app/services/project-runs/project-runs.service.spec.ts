import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ConfigService } from '@observability-ui/core';
import { ProjectRunsService } from './project-runs.service';

describe('Project Runs Service', () => {
  let service: ProjectRunsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        ProjectRunsService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    service = TestBed.inject(ProjectRunsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
