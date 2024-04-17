import { TestBed } from '@angular/core/testing';
import { AgentService, AgentStore } from '../../';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('agent.store', () => {

  let store: AgentStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        AgentStore,
        MockProvider(AgentService)
      ],
    });

    store = TestBed.inject(AgentStore);

  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

});
