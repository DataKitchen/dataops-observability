import { Component } from '@angular/core';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { AsyncPipe, JsonPipe, NgIf } from '@angular/common';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { TranslationModule } from '@observability-ui/translate';
import { APIKeysStore } from '../api-keys.store';
import { toSignal } from '@angular/core/rxjs-interop';
import { ProjectStore } from '@observability-ui/core';
import { pick, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { FormsModule, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { CheckboxFieldModule, CodeSnippetComponent, DkTooltipModule, TextFieldModule } from '@observability-ui/ui';
import { MatLegacyProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { ApiKeyServiceFields } from '../../integrations/tools/abstract-tool.directive';

@Component({
  selector: 'shell-add-api-key-modal-component',
  templateUrl: 'add-api-key-modal.component.html',
  imports: [ MatDialogModule, MatIconModule, MatLegacyFormFieldModule, MatDialogModule, AsyncPipe, MatLegacyButtonModule, NgIf, TranslationModule, FormsModule, ReactiveFormsModule, TextFieldModule, JsonPipe, MatLegacyProgressSpinnerModule, CodeSnippetComponent, DkTooltipModule, CheckboxFieldModule ],
  standalone: true,
  styleUrls: [ 'add-api-key-modal.component.scss' ]
})
export class AddApiKeyModalComponent {
  loading = toSignal(this.store.getLoadingFor('create'));
  project = toSignal(this.projectStore.current$);
  token = toSignal(this.store.token$);

  formGroup = new TypedFormGroup<ApiKeyServiceFields>({
    name: new TypedFormControl<string>(null, [ Validators.required ]),
    expires_after_days: new TypedFormControl<number>(null, [ Validators.required, Validators.pattern('^[0-9]+$'), Validators.min(1) ]),
    allow_send_events: new TypedFormControl<boolean>(true),
    allow_manage_components: new TypedFormControl<boolean>(false),
    allow_agent_api: new TypedFormControl<boolean>(false),
  }, [this.shouldHaveOne()]);

  constructor(
    private store: APIKeysStore,
    private projectStore: ProjectStore,
  ) {}

  createKey() {
    const form = pick(this.formGroup.value, ['name', 'expires_after_days']);
    const allowed_services = [];

    if (this.formGroup.value.allow_send_events) {
      allowed_services.push('EVENTS_API');
    }

    if (this.formGroup.value.allow_manage_components) {
      allowed_services.push('OBSERVABILITY_API');
    }

    if (this.formGroup.value.allow_agent_api) {
      allowed_services.push('AGENT_API');
    }

    this.store.dispatch('create', { ...form, allowed_services } as any, this.project().id);
  }

  private shouldHaveOne(): ValidatorFn {
    return (control) => {
      const { allow_send_events, allow_manage_components, allow_agent_api } = (control as TypedFormGroup<ApiKeyServiceFields>).controls;
      if (allow_manage_components.value || allow_agent_api.value || allow_send_events.value) {
        return null;
      }

      return { required: true };
    };

  }
}
