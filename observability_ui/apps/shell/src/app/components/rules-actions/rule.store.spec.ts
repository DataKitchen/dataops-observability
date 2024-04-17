import { TestBed } from '@angular/core/testing';
import { RuleStore } from './rule.store';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { ConfigService } from '@observability-ui/core';
import { RuleService } from './rule.service';
import { Rule } from './rule.model';
import { TestScheduler } from '@datakitchen/rxjs-marbles';

describe('rule.store', () => {

  const rule: Omit<Rule, 'id'> = {
    rule_schema: 'simple_v1',
    rule_data: {
      when: 'all',
      conditions: []
    },
    action: 'action',
    action_args: 'args',
    parentId: 'id',
  };

  let store: RuleStore;
  let service: Mocked<RuleService>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RuleStore,
        MockProvider(ConfigService, class {
          get: () => 'base_url';
        }),
        MockProvider(RuleService, class {
          // overrides
        })
      ],
    });

    store = TestBed.inject(RuleStore);
    service = TestBed.inject(RuleService) as Mocked<RuleService>;

  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

  describe('#saveOne', () => {

    it('should call service', () => {
      store.saveOne({...rule});
      expect(service.create).toHaveBeenCalled();
    });

    it('should reduce state', () => {
      const state = store.onSaveOne({list: [], total: 0}, {id: 'rule_id', ...rule});

      expect(state).toEqual({
        list: [{id: 'rule_id', ...rule}],
        total: 1,
      });
    });
  });

  describe('#updateOne', () => {

    it('should call service', () => {
      store.updateOne({id: 'id', ...rule});
      expect(service.update).toHaveBeenCalled();
    });

    it('should reduce state', () => {
      const state = store.onUpdateOne({
        list: [{id: 'rule_id', ...rule}],
        total: 1
      }, {id: 'rule_id', ...rule, action: 'action_updated'});

      expect(state).toEqual({
        list: [
          {
            id: 'rule_id',
            ...rule,
            action: 'action_updated',
          }
        ],
        total: 1,
      });
    });
  });

  describe('#reset', () => {
    it('should not do anything', () => {
      TestScheduler.expect$(store.reset()).toBe('(a|)', { a: undefined });
    });

    it('should reset the state', () => {
      expect(store.onReset()).toEqual({
        list: [], total: 0,
      });
    });
  });
});
