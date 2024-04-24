import { TestBed } from '@angular/core/testing';
import { AgentService } from './agent.service';
import { HttpClient } from '@angular/common/http';
import { ConfigService } from '../../../config';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('agent.service', () => {

  let service: AgentService;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [
        AgentService,
        MockProvider(ConfigService),
        MockProvider(HttpClient),
      ],
    });


    service = TestBed.inject(AgentService);

  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

});
