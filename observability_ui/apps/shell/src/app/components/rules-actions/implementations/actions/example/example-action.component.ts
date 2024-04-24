import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AbstractAction } from '../../../abstract-action.directive';
import { MatExpansionModule } from '@angular/material/expansion';
import { ActionTemplateComponent } from '../../../action/action-template.component';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'example-action',
  template: `

    <action-template [action]="this">
      <div class="title">Example Action</div>
      <div class="description" *ngIf="!editMode">
        <i>{{this.form.value}}</i>
      </div>

      <mat-form-field>
        <mat-label></mat-label>
        <input matInput [formControl]="form">
      </mat-form-field>

    </action-template>
  `,
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatExpansionModule,
    ActionTemplateComponent,
  ],
})
export class ExampleActionComponent extends AbstractAction {
  static override label = 'Example Action';
  static override _type = 'EXAMPLE_ACTION';

  version = 'v1';

  form = new FormControl<string>('', [ Validators.required ]);
}
