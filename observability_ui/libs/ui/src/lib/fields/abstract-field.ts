import { Directive, EventEmitter, Input, OnInit, Optional, Output, Self } from '@angular/core';
import { ControlValueAccessor, UntypedFormControl, NgControl } from '@angular/forms';
import { CoreComponent } from '@datakitchen/ngx-toolkit';
import { noop } from 'rxjs';

@Directive()
export abstract class AbstractField<T = any> extends CoreComponent implements ControlValueAccessor, OnInit {

  @Input() disabled!: boolean;
  // I think this should actually be change like `mat-checkbox` has the `change` output
  // eslint-disable-next-line @angular-eslint/no-output-native
  @Output() change: EventEmitter<T> = new EventEmitter<T>();

  protected onChange: (value: T) => void = noop;

  protected onTouched: (value: T) => void = noop;

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  public writeValue(value: any): void {
   noop();
  }

  get control(): UntypedFormControl {
    return this.ngControl?.control as unknown as UntypedFormControl;
  }

  constructor(
    @Self() @Optional() protected ngControl?: NgControl,
  ) {
    super();
    if (ngControl) {
      ngControl.valueAccessor = this;
    }
  }

  registerOnChange(fn: (value: T) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }
}
