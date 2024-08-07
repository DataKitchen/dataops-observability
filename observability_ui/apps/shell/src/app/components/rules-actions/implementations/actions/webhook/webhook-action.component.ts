import { Component } from '@angular/core';
import { FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { AbstractAction, stringify } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { NgxMonacoEditorModule } from '@datakitchen/ngx-monaco-editor';
import { ActionTemplateComponent } from '../../../action/action-template.component';
import { Rule } from '../../../rule.model';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { NgForOf, NgIf } from '@angular/common';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'webhook-action',
  template: `
    <div *ngIf="!editMode"
      class="display__box">
      <span class="display__label">Send web request to</span>
      <span class="display__url">{{form.controls.url.value}}</span>
    </div>

    <action-template *ngIf="editMode"
      [action]="this">
      <div class="title">
        Send Web Request
      </div>

      <div class="description">
        <i>{{form.controls.url.value}}</i>
      </div>

      <div class="flex-column controls">
        <div class="help-link text-caption--secondary">
          Learn more about
          <a href="https://docs.datakitchen.io/article/dataops-observability-help/web-request" target="_blank">
            configuring webhooks.
            <mat-icon inline>open_in_new</mat-icon>
          </a>
        </div>


        <div class="flex-row">
          <mat-form-field class="pr-1 method-field">
            <mat-label>Method</mat-label>

            <mat-select [formControl]="form.controls.method">
              <mat-option *ngFor="let method of methods" [value]="method">
                {{method}}
              </mat-option>
            </mat-select>

          </mat-form-field>

          <mat-form-field class="fx-flex">
            <mat-label>URL</mat-label>
            <input matInput
              placeholder=""
              [formControl]="form.controls.url"
              autofocus>


            <mat-error *ngIf="form.controls.url.hasError('required')">
              Field is required
            </mat-error>

          </mat-form-field>

        </div>


        <mat-form-field>
          <mat-label>Payload</mat-label>
          <ngx-monaco-editor [formControl]="form.controls.payload"></ngx-monaco-editor>

        </mat-form-field>

        <mat-form-field>
          <mat-label>Headers</mat-label>
          <ngx-monaco-editor [formControl]="form.controls.headers"></ngx-monaco-editor>
        </mat-form-field>

      </div>
    </action-template>

  `,
  standalone: true,
  imports: [
    ActionTemplateComponent,
    ReactiveFormsModule,
    FormsModule,
    MatInputModule,
    MatIconModule,
    NgxMonacoEditorModule,
    ReactiveFormsModule,
    MatLegacySelectModule,
    NgForOf,
    NgIf,
  ],
  styles: [
    `
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
      .display__url {
        font-style: italic;
        word-break: break-word;
      }
      ngx-monaco-editor {
        border: var(--border);
        border-radius: var(--border-radius);
      }

      .controls > *:not(:last-child) {
        padding-bottom: 16px;
      }

      .label {
        font-size: 14px;
        margin-bottom: 8px;
      }

      .help-link {
        display: flex;
        flex-direction: row;
      }

      .help-link > a {
        display: flex;
        flex-direction: row;
        padding-left: 3px;
      }

      .method-field {
        width: 85px;
      }
    `
  ]
})
export class WebhookActionComponent extends AbstractAction<Rule> {
  static override label = 'Web Request';
  static override _type = 'CALL_WEBHOOK';

  version = 'v1';

  form = new TypedFormGroup<{
    method: string,
    url: string;
    payload: string;
    headers: string;
  }>({
    method: new TypedFormControl<string>('POST', Validators.required),
    url: new TypedFormControl<string>(null, [
      Validators.required,
    ]),
    payload: new TypedFormControl<string>('{}'),
    headers: new TypedFormControl<string>('[]'),
  });

  methods = [ 'POST', 'PUT', 'GET', 'PATCH', 'DELETE' ];

  override parse({method, url, payload, headers }: {
    method: string;
    url: string;
    payload: object|null;
    headers: object|null;
  }) {

    super.parse({
      method,
      url,
      payload: stringify(payload, true),
      headers: stringify(headers, true),
    });

  }

  override toJSON(): Pick<Rule, 'action' | 'action_args'> {

    const { action } = super.toJSON();

    return {
      action,
      action_args: {
        method: this.form.controls.method.value,
        url: this.form.controls.url.value,
        // form state is a string representing a json object we need to parse
        // it in order to send it to BE
        payload: JSON.parse(this.form.controls.payload.value||null),
        headers: JSON.parse(this.form.controls.headers.value||null),
      }
    };
  }

}
