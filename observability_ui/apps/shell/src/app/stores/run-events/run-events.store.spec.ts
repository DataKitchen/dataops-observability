import { TestBed } from '@angular/core/testing';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ConfigService } from '@observability-ui/core';
import { RunEventsStore } from './run-events.store';
import { RunEventsService } from '../../services/run-events/run-events.service';

describe('run-events.store', () => {

  let store: RunEventsStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RunEventsStore,
        MockProvider(ConfigService, class {
          get: () => 'base_url';
        }),
        MockProvider(RunEventsService, class {
          // overrides
        })
      ],
    });

    store = TestBed.inject(RunEventsStore);

  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

});
