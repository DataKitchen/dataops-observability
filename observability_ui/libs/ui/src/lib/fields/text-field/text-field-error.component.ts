import { Component, Input, TemplateRef, ViewChild } from '@angular/core';

@Component({
  selector: 'text-field-error',
  template: `
    <ng-template>
        <ng-content></ng-content>
    </ng-template>
  `
})
export class TextFieldErrorComponent {

  @Input() type!: string;

  @ViewChild(TemplateRef, { static: true }) template!: TemplateRef<TextFieldErrorComponent>;
}
