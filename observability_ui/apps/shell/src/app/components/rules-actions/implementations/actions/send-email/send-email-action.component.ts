import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { AbstractAction, CustomValidators, TaskStatusEmailTemplate } from '@observability-ui/core';
import { Rule, RuleType } from '../../../rule.model';
import { AbstractRule } from '../../../abstract.rule';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatLegacyChipsModule as MatChipsModule } from '@angular/material/legacy-chips';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { AsyncPipe, JsonPipe, NgForOf, NgIf } from '@angular/common';
import { ActionTemplateComponent } from '../../../action/action-template.component';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'send-email-action',
  template: `
    <div *ngIf="!editMode"
      class="display__box">
      <span class="display__label">Send email to</span>
      <div class="display__chips">
        <mat-chip-list>
          <ng-container *ngFor="let email of form.controls.recipients.value?.split(',')">
            <mat-chip [disabled]="true"
              class="email-chip"
              *ngIf="email">
              {{email}}
            </mat-chip>
          </ng-container>
        </mat-chip-list>
      </div>
    </div>

    <action-template *ngIf="editMode"
      [action]="this">
      <div class="title">Send Email</div>
      <div class="description">
        {{form.controls.recipients.value?.split(',').length || 0}} recipients
      </div>

      <mat-form-field>
        <mat-label>Recipients</mat-label>
        <textarea [formControl]="form.controls.recipients"
          rows="3"
          matInput></textarea>
          <mat-hint>comma separated list</mat-hint>
      </mat-form-field>
    </action-template>

  `,
  standalone: true,
  styles: [ `
    .display__box {
      border: 1px solid rgba(0, 0, 0, 0.12);
      border-radius: 4px;
      padding: 8px 16px;
      display: flex;
    }
    .display__label {
      flex: auto 0 0;
      align-self: center;
      margin-right: 12px;
    }
    .display__chips {
      max-height: 200px;
      overflow: auto;
    }
    mat-form-field {
      display: block;
    }
    .email-chip {
      font-size: 14px;
      font-weight: 400;
      padding: 6px 12px;
      min-height: 24px;
      background-color: #f5f5f5;
      color: black;
      opacity: 1 !important;
    }
    :host ::ng-deep .mat-chip-list-wrapper {
      margin: 0;
    }
  ` ],
  imports: [
    MatExpansionModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    NgIf,
    NgForOf,
    ActionTemplateComponent,
    JsonPipe,
    AsyncPipe,
  ]
})
export class SendEmailActionComponent extends AbstractAction<AbstractRule> {
  static override label = 'Send Email';
  static override _type = 'SEND_EMAIL';

  version = 'simple_v1';

  form = new FormGroup({
    template: new FormControl<string>(''),
    recipients: new FormControl<string>('', [ CustomValidators.required, CustomValidators.emails() ]),
  });

  override parse({ template, recipients }: { template?: string; recipients: string[] }) {
    if (template) {
      this.form.patchValue({ template }, { emitEvent: false });
    }
    this.form.patchValue({ recipients: recipients.join(', ') });
  }

  override hydrateFromRule(rule: AbstractRule): void {
    const ruleType = rule.type as RuleType;
    const { matches } = rule.form.value;

    let template;

    if (ruleType === 'task_status') {
      template = TaskStatusEmailTemplate[matches];
    } else {
      template = ruleType;
    }

    this.form.patchValue({ template });
  }

  override toJSON(): Pick<Rule, 'action' | 'action_args'> {
    const { template, recipients } = this.form.value;
    const optionalArgs: { template?: string } = {};
    if (template) {
      optionalArgs.template = template;
    }

    return {
      action: this.type,
      action_args: {
        ...optionalArgs,
        recipients: recipients?.split(',')
          // remove empty strings
          .filter((email) => !!email)
          .map((email) => email.trim()) || [],
      }
    };
  }
}
