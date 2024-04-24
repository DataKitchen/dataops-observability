import { Component } from '@angular/core';
import { EntitiesResolver, EmailAction, ActionType } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { AsyncPipe, NgIf } from '@angular/common';
import { MatCardEditComponent, TextFieldModule } from '@observability-ui/ui';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { filter, tap } from 'rxjs';
import { EmailActionStore } from './email-action.store';

@Component({
  selector: 'shell-email-action',
  templateUrl: 'email-action.component.html',
  styleUrls: [ 'email-action.component.scss' ],
  standalone: true,
  imports: [
    NgIf,
    AsyncPipe,
    MatCardEditComponent,
    ReactiveFormsModule,
    TextFieldModule,
  ]
})
export class EmailActionComponent {
  emailAction = toSignal(this.store.emailAction$.pipe(
    tap(emailAction => {
      const { smtp_config } = emailAction?.action_args || {};
      this.form = new TypedFormGroup<{
        id: string,
        endpoint: string,
        port: number,
        username: string,
        password: string,
        from_address: string,
      }>({
        id: new TypedFormControl<string>(emailAction?.id),
        endpoint: new TypedFormControl<string>(smtp_config?.endpoint, Validators.required),
        port: new TypedFormControl<number>(smtp_config?.port, Validators.required),
        username: new TypedFormControl<string>(smtp_config?.username, Validators.required),
        password: new TypedFormControl<string>(smtp_config?.password, Validators.required),
        from_address: new TypedFormControl<string>(smtp_config?.endpoint ? emailAction.action_args.from_address : null, Validators.required),
      });
    })
  ));
  saving = toSignal(this.store.getLoadingFor('update'));
  
  form: FormGroup;

  constructor(
    private store: EmailActionStore,
    private entities: EntitiesResolver,
  ) {
    this.entities.company$
      .pipe(
        filter(company => !!company),
        takeUntilDestroyed(),
      )
      .subscribe(({ id }) => this.store.dispatch('get', id));
  }

  saveEmailAction() {
    const { id, endpoint, port, username, password, from_address } = this.form.value;
    this.store.dispatch('update', {
      id,
      name: 'Send Email',
      action_impl: ActionType.SendEmail,
      action_args: {
        template: 'NotifyTemplate',
        recipients: [],
        from_address,
        smtp_config: { endpoint, port, username, password },
      },
    });
  }

  cancelEmailActionChanges(emailAction: EmailAction): void {
    const { smtp_config } = emailAction?.action_args || {};
    this.form.patchValue({ 
      endpoint: smtp_config?.endpoint, 
      port: smtp_config?.port, 
      username: smtp_config?.username, 
      password: smtp_config?.password, 
      from_address: smtp_config?.endpoint ? emailAction.action_args.from_address : null, 
    });
  }
}
