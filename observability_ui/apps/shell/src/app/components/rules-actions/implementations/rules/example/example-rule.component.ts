import { Component } from '@angular/core';
import { TextFieldModule } from '@observability-ui/ui';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { AbstractRule } from '../../../abstract.rule';
import { ExampleRuleLabelComponent } from './example-rule-label.component';
import { NgIf } from '@angular/common';


@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'example-rule',
  template: `
    <ng-container *ngIf="editMode">
        <text-field label="Example" [formControl]="form"></text-field>
    </ng-container>

    <ng-container *ngIf="!editMode">
      My name is: {{form.getRawValue()}}
    </ng-container>
  `,
  standalone: true,
  imports: [
    TextFieldModule,
    ReactiveFormsModule,
    NgIf
  ]
})
export class ExampleRuleComponent extends AbstractRule {
  static override labelTpl = ExampleRuleLabelComponent;
  static override _type = 'example_rule';

  form = new FormControl<string>('', [ Validators.required ]);

}
