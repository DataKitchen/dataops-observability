import { Component } from '@angular/core';
import { Project, ProjectStore } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { AsyncPipe, NgIf } from '@angular/common';
import { CreatedByComponent, DetailsHeaderModule, MatCardEditComponent, TextFieldModule } from '@observability-ui/ui';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule } from '@angular/material/legacy-input';
import { tap } from 'rxjs';
import { EmailActionComponent } from '../../components/email-action/email-action.component';

@Component({
  selector: 'shell-project-settings',
  templateUrl: 'settings.component.html',
  styleUrls: [ 'settings.component.scss' ],
  standalone: true,
  imports: [
    NgIf,
    AsyncPipe,
    DetailsHeaderModule,
    MatCardEditComponent,
    ReactiveFormsModule,
    CreatedByComponent,
    MatLegacyFormFieldModule,
    MatLegacyInputModule,
    TextFieldModule,
    EmailActionComponent,
  ]
})
export class SettingsComponent {
  project = toSignal(this.store.current$.pipe(
    tap((project) => {
      this.form = new TypedFormGroup<{
        id: string,
        name: string,
        description: string
      }>({
        id: new TypedFormControl<string>(project.id),
        name: new TypedFormControl<string>(project.name),
        description: new TypedFormControl<string>(project.description)
      });
    })
  ));
  saving = toSignal(this.store.getLoadingFor('updateOne'));

  form: FormGroup;

  constructor(
    private store: ProjectStore,
  ) {
  }

  saveInfo() {
    this.store.dispatch('updateOne', {
      ...this.form.value,
    });
  }

  cancelInfoChanges(project: Project): void {
    this.form.patchValue({ name: project.name, description: project.description });
  }
}
