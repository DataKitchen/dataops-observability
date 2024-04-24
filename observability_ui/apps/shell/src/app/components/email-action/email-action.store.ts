import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { Effect, makeStore, Reduce, Store } from '@microphi/store';
import { ActionType, CompanyService, EmailAction } from '@observability-ui/core';

interface EmailActionState {
  emailAction: EmailAction,
}


interface EmailActionActions {
  get: (companyId: string) => Observable<EmailAction>;
  update: (emailAction: EmailAction) => Observable<EmailAction>;
}

@Injectable({providedIn: 'root'})
export class EmailActionStore extends Store<EmailActionState, EmailActionActions> implements makeStore<EmailActionState, EmailActionActions> {

  emailAction$ = this.select(state => state.emailAction);
  isConfigured$ = this.select(state => !!state.emailAction.action_args?.smtp_config?.endpoint);

  constructor(
    private companyService: CompanyService,
  ) {
    super({
      emailAction: undefined,
    });
  }

  @Effect()
  get(companyId: string): Observable<EmailAction> {
    return this.companyService.getActions({
      parentId: companyId,
      page: 0,
      count: 1,
      filters: { action_impl: ActionType.SendEmail },
    }).pipe(
      map(response => response.entities[0]),
    );
  }

  @Reduce()
  onGet(state: EmailActionState, emailAction: EmailAction): EmailActionState {
    return {
      ...state,
      emailAction,
    };
  }

  @Effect()
  update(emailAction: EmailAction): Observable<EmailAction> {
    return this.companyService.updateAction(emailAction);
  }

  @Reduce()
  onUpdate(state: EmailActionState, emailAction: EmailAction): EmailActionState {
    return {
      ...state,
      emailAction,
    };
  }
}
