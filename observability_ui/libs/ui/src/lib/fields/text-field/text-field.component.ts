import { Component, ContentChildren, Input, QueryList } from '@angular/core';
import { AbstractField } from '../abstract-field';
import { TextFieldErrorComponent } from './text-field-error.component';

@Component({
  selector: 'text-field',
  templateUrl: './text-field.component.html',
  styleUrls: [ './text-field.component.scss' ]
})
export class TextFieldComponent extends AbstractField<any> {
  @Input() label!: string;
  @Input() placeholder!: string;
  @Input() hint!: string;

  @Input() type!: 'search' | 'text' | 'password' | 'number';
  @ContentChildren(TextFieldErrorComponent) errors!: QueryList<TextFieldErrorComponent>;
  @Input() autofocus: boolean = false;
}
