import { TestBed } from '@angular/core/testing';
import { APIKeysStore } from './api-keys.store';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { APIKeysService } from './api-keys.service';

describe('api-keys.store', () => {

  let store: APIKeysStore;

  beforeEach(async () => {
    await TestBed.configureTestingModule({

      providers: [
        APIKeysStore,
        MockProvider(APIKeysService)
      ],
    });

    store = TestBed.inject(APIKeysStore);

  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

});
