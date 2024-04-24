import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ConfigService } from '@observability-ui/core';
import { RunEventsService } from './run-events.service';

describe('Run Events Service', () => {
  let service: RunEventsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        RunEventsService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    service = TestBed.inject(RunEventsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
