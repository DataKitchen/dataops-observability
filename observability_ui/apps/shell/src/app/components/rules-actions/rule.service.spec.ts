import { RuleService } from './rule.service';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ConfigService } from '@observability-ui/core';

describe('rule.service', () => {

  let service: RuleService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      providers: [
        RuleService,
        MockProvider(ConfigService, class {
          get: () => 'base_url';
        })
      ],
    });

    service = TestBed.inject(RuleService);

  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

});
