import { TestBed } from '@angular/core/testing';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ConfigService } from '@observability-ui/core';
import { RunTasksStore } from './run-tasks.store';
import { RunTasksService } from '../../services/run-tasks/run-tasks.service';

describe('run-task.store', () => {

  let store: RunTasksStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RunTasksStore,
        MockProvider(ConfigService, class {
          get: () => 'base_url';
        }),
        MockProvider(RunTasksService, class {
          // overrides
        })
      ],
    });

    store = TestBed.inject(RunTasksStore);

  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

});
