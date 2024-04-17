import { Injectable } from '@angular/core';
import { Effect, makeStore, Reduce } from '@microphi/store';
import { EntityActions, EntityState, EntityStore, Optionalize } from '@observability-ui/core';
import { Rule } from './rule.model';
import { RuleService } from './rule.service';
import { Observable } from 'rxjs';

interface RuleActions extends EntityActions<Rule> {
  saveOne: (rule: Optionalize<Rule, 'id'>) => Observable<Rule>;
  updateOne: (rule: Pick<Rule, 'id'|'action_args'|'action'|'rule_data'|'component'>) => Observable<Rule>;
}

@Injectable({
  providedIn: 'root',
})
export class RuleStore extends EntityStore<EntityState<Rule>, RuleActions> implements makeStore<EntityState<Rule>, RuleActions> {

  constructor(protected service: RuleService) {
    super({
      list: [],
      total: 0,
    });
  }

  @Effect()
  saveOne({parentId, ...rule}: Optionalize<Rule, 'id'>): Observable<Rule> {
    return this.service.create(rule, parentId);
  }

  @Reduce()
  onSaveOne(state: EntityState<Rule>, payload: Rule): EntityState<Rule> {
    return {
      ...state,
      list: [ ...state.list, payload ],
      total: state.total + 1,
    };
  }

  @Effect()
  updateOne(rule: Pick<Rule, 'id'|'action_args'|'action'|'rule_data'>): Observable<Rule> {
    return this.service.update(rule);
  }

  @Reduce()
  onUpdateOne(state: EntityState<Rule>, payload: Rule): EntityState<Rule> {
    const idx = state.list.findIndex(({id}) => id === payload.id);
    state.list[idx] = payload;

    return state;
  }
}
