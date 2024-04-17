import { AfterViewInit, Component, Input, Optional, Self } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NgControl, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { CustomValidators } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { AbstractField, CheckboxFieldModule, DkTooltipModule, TextFieldModule } from '@observability-ui/ui';
import { ApiKeyServiceFields } from '../tools/abstract-tool.directive';

@Component({
  selector: 'shell-service-key-form',
  template: `
    <label>New API Key</label>

    <div [formGroup]="form">
      <text-field formControlName="name"
        label="Name"
        type="text">
        <text-field-error type="required">A name is required</text-field-error>
        <text-field-error type="maxLength">A maximun of 255 characters is allowed</text-field-error>
      </text-field>
      <text-field formControlName="expires_after_days"
        label="Expires after (days)"
        type="number">
        <text-field-error type="required">A value of 1 or greater is required</text-field-error>
        <text-field-error type="min">A value of 1 or greater is required</text-field-error>
      </text-field>
      <text-field formControlName="description"
        label="Description"
        hint="{{ form.value.description?.length ?? 0 }}/255"
        type="text">
        <text-field-error type="maxLength">A maximun of 255 characters is allowed</text-field-error>
      </text-field>
    </div>

    <div>
      <checkbox-field [formControl]="form.controls.allow_send_events">
        Send events
      </checkbox-field>
      <checkbox-field [formControl]="form.controls.allow_manage_components">
        Manage entities <span class="tag filled" dkTooltip="Access to—and use of—the Observability API is in beta. It introduces some ability to manage system entities, such as components and journeys.">Beta</span>
      </checkbox-field>
      <checkbox-field [formControl]="form.controls.allow_agent_api">
        Transmit heartbeat
        <span class="tag filled" dkTooltip="Service account keys created for agents must include heartbeat transmission.">Agents</span>
      </checkbox-field>
    </div>


  `,
  styles: [
    `
      label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
        color: var(--text-secondary-color);
      }

      div {
        display: flex;

        text-field + text-field {
          margin-left: 8px;
        }

        checkbox-field + checkbox-field {
          margin-left: 24px;
        }
      }
    `
  ],
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TextFieldModule,
    CheckboxFieldModule,
    DkTooltipModule,
  ],
})
export class ServiceKeyFormComponent extends AbstractField<{name: string; description?: string; expires_after_days: number; allow_send_events: boolean; allow_manage_components: boolean}> implements AfterViewInit {
  @Input() existing: string[] = [];

  form = new TypedFormGroup<ApiKeyServiceFields>({
    name: new TypedFormControl<ApiKeyServiceFields["name"]>('', [ Validators.required, Validators.maxLength(255), CustomValidators.forbiddenNames(this.existing) ]),
    description: new TypedFormControl<string>('', [ Validators.maxLength(255) ]),
    expires_after_days: new TypedFormControl<ApiKeyServiceFields["expires_after_days"]>(0, [ Validators.required, Validators.min(1) ]),
    allow_send_events: new TypedFormControl<ApiKeyServiceFields["allow_send_events"]>({
      value: true,
      disabled: true
    }),
    allow_manage_components: new TypedFormControl<ApiKeyServiceFields["allow_manage_components"]>(true),
    allow_agent_api: new TypedFormControl<ApiKeyServiceFields["allow_agent_api"]>({
      value: true,
      disabled: true
    }),
  });

  private validator = (): ValidationErrors | null => {
    return {...this.form.controls['name'].errors, ...this.form.controls['expires_after_days'].errors};
  };

  constructor(
    @Self() @Optional() protected override ngControl: NgControl,
  ) {
    super(ngControl);

    this.form.valueChanges.pipe(
      takeUntilDestroyed(),
    ).subscribe((value) => {
      this.onChange(value);
    });
  }

  public override ngAfterViewInit(): void {
    super.ngAfterViewInit();

    this.control.clearValidators();
    this.control.addValidators(this.validator);
    this.control.updateValueAndValidity();
  }

  override writeValue(value: ApiKeyServiceFields): void {
    this.form.patchValue(value);
  }
}
