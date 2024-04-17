import { TestBed } from '@angular/core/testing';
import { APIKeysService } from './api-keys.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ConfigService } from '@observability-ui/core';

describe('api-keys.service', () => {

  let service: APIKeysService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      providers: [
        APIKeysService,
        MockProvider(ConfigService, class {
          get: () => 'base_url';
        })

      ],
    });

    service = TestBed.inject(APIKeysService);

  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

});
