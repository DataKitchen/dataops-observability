/* eslint-disable @typescript-eslint/no-unused-vars,@angular-eslint/no-input-rename,@typescript-eslint/no-empty-function */
import { Directive, ElementRef, HostBinding, HostListener, Inject, Input, OnDestroy, Optional, Self } from '@angular/core';
import { ControlValueAccessor, NgControl } from '@angular/forms';
import { MAT_LEGACY_FORM_FIELD as MAT_FORM_FIELD, MatLegacyFormField as MatFormField, MatLegacyFormFieldControl as MatFormFieldControl } from '@angular/material/legacy-form-field';
import { TypedFormControl } from '@datakitchen/ngx-toolkit';
import { Subject } from 'rxjs';
import { BooleanInput, coerceBooleanProperty } from '@angular/cdk/coercion';
import { FocusMonitor } from '@angular/cdk/a11y';

@Directive()
export abstract class AbstractMatFormFieldControl<T> implements ControlValueAccessor, MatFormFieldControl<T>, OnDestroy {

  readonly autofilled!: boolean;

  static nextId = 0;

  abstract getEmptyState(): boolean;
  abstract getValue(): T;
  abstract setValue(v: T): void;

  /**
   * This is just a string used to identify the inner container that will
   * be used to set `setDescribedByIds` for accessibility purpose.
   * I.e.:
   * when an element with `.${this.controlType}-container` class is available
   * then it will be used to be "described" by its ids.
   *
   */
  abstract controlType: string ;

  abstract _control: TypedFormControl<T>;

  stateChanges = new Subject<void>();
  focused = false;
  touched = false;

  @HostBinding('id')
  id = `${this.constructor.name}-${AbstractMatFormFieldControl.nextId++}`;
  onChange = (_: T|null) => {};
  onTouched = () => {};

  get empty() {
    return this.getEmptyState();
  }

  @HostBinding('class.should-float-label')
  get shouldLabelFloat() {
    return this.focused || !this.empty;
  }

  @Input('aria-describedby') userAriaDescribedBy!: string;

  @Input()
  get placeholder(): string {
    return this._placeholder;
  }

  set placeholder(value: string) {
    this._placeholder = value;
    this.stateChanges.next();
  }

  private _placeholder!: string;

  @Input()
  get required(): boolean {
    return this._required;
  }

  set required(value: BooleanInput) {
    this._required = coerceBooleanProperty(value);
    this.stateChanges.next();
  }

  private _required = false;

  @Input()
  get disabled(): boolean {
    return this._disabled;
  }

  set disabled(value: BooleanInput) {
    this._disabled = coerceBooleanProperty(value);
    this._disabled ? this._control.disable() : this._control.enable();
    this.stateChanges.next();
  }

  private _disabled = false;

  @Input()
  get value(): T {
    return this.getValue();
  }
  set value(value: T) {
    this.setValue(value);
    this.stateChanges.next();
  }

  get errorState(): boolean {
    return this._control.invalid && this.touched;
  }


  constructor(
    private _focusMonitor: FocusMonitor,
    private _elementRef: ElementRef<HTMLElement>,
    @Optional() @Inject(MAT_FORM_FIELD) public _formField: MatFormField,
    @Optional() @Self() public ngControl: NgControl,
  ) {

    if (this.ngControl != null) {
      this.ngControl.valueAccessor = this;
    }
  }

  ngOnDestroy() {
    this.stateChanges.complete();
    this._focusMonitor.stopMonitoring(this._elementRef);
  }

  setDescribedByIds(ids: string[]) {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const controlElement = this._elementRef.nativeElement.querySelector(`.${this.controlType}-container`)!;
    controlElement?.setAttribute('aria-describedby', ids.join(' '));
  }

  onContainerClick() {
    console.warn('Not Implemented! Add your logic if you find a ');
  }

  writeValue(value: T): void {
    this.value = value;
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  onInput(): void {
    this.onChange(this.value);
  }

  @HostListener('focusin')
  onFocusIn() {
    if (!this.focused) {
      this.focused = true;
      this.stateChanges.next();
    }
  }

  @HostListener('focusout')
  onFocusOut() {
    this.touched = true;
    this.focused = false;
    this.onTouched();
    this.stateChanges.next();
  }

}
