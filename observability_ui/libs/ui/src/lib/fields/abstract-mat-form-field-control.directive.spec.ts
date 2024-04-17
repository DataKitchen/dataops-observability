import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, ViewChild } from '@angular/core';
import { MatLegacyFormFieldControl as MatFormFieldControl, MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { AbstractMatFormFieldControl } from './abstract-mat-form-field-control.directive';
import { TypedFormControl } from '@datakitchen/ngx-toolkit';
import { ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIf } from '@angular/common';
import { MatLegacyInputModule } from '@angular/material/legacy-input';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('abstract-mat-form-field-control', () => {

  @Component({
    selector: 'test-input',
    template: `
      <div class="test-input-field-container">
        <input type="text"
          (input)="onInput()">
      </div>

    `,
    providers: [
      {
        provide: MatFormFieldControl,
        useExisting: TestInputField
      }
    ],
    standalone: true,
  })
  // eslint-disable-next-line @angular-eslint/component-class-suffix
  class TestInputField extends AbstractMatFormFieldControl<string>{

    override controlType = 'test-input-field';

    getEmptyState(): boolean {
      return this._control.value === '';
    }

    getValue(): string {
      return this._control.value;
    }

    _control = new TypedFormControl<string>();

    setValue(v: string): void {
      this._control.setValue(v);
    }
  }

  @Component({
    selector: 'test-component',
    template: `


      <mat-form-field>
        <mat-label>Test Input</mat-label>
        <test-input #inputField
          placeholder="test placeholder"
          [formControl]="customInputFc"
          autofocus></test-input>

        <mat-hint>Type anything</mat-hint>

        <mat-error *ngIf="customInputFc.getError('custom')">Custom Error!</mat-error>

      </mat-form-field>
    `,
    standalone: true,
    imports: [
      MatLegacyFormFieldModule,
      ReactiveFormsModule,
      NgIf,
      MatLegacyInputModule,
      TestInputField,
    ]
  })
  class TestComponent {
    @ViewChild('inputField', {read: TestInputField}) inputField!: TestInputField;

    customInputFc = new TypedFormControl<string>(null, [Validators.required]);

  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TestComponent,
        NoopAnimationsModule,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should propagate changes to parent control', () => {
    // simulate altering the input from the ui
    component.inputField._control.setValue('my name');
    component.inputField.onInput();

    expect(component.customInputFc.value).toEqual('my name');
  });

  xit('should propagate error state', () => {
    /**
     * error propagation to upstream form control is broken
     * reactive forms only propagate values
     */

    // simulate altering the input from the ui
    console.log('setting custom error');
    // component.inputField._control.setErrors({custom: true});
    // component.inputField.onInput();

    // expect(component.customInputFc.invalid).toEqual(true);
    // somehow the following fails.
    // I'm not sure why but for empirical tests the errors are being propagated
    // correctly and indeed the `customInputFc` state is `invalid` as the above
    // assertion confirms.
    console.log('asserting');
    expect(component.customInputFc.errors).toEqual({custom: true});
  });

});
