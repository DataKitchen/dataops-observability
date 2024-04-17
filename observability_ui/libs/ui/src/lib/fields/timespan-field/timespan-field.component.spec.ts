import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TimespanFieldComponent } from './timespan-field.component';
import { MockModule, MockPipe } from 'ng-mocks';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { TextFieldModule } from '../text-field/text-field.module';
import { TranslatePipeMock } from '@observability-ui/translate';
import { ReactiveFormsModule } from '@angular/forms';
import { TimespanPipe } from './timespan.pipe';
import { Component, ViewChild } from '@angular/core';
import { TypedFormControl } from '@datakitchen/ngx-toolkit';

describe('TimespanFieldComponent', () => {
  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  @Component({
    selector: 'test-component',
    template: `
      <timespan-field [formControl]="fc"></timespan-field>
    `
  })
  class TestComponent {
    @ViewChild(TimespanFieldComponent) field: TimespanFieldComponent;

    fc = new TypedFormControl<{margin: number}>();
  }

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        TimespanFieldComponent,
        TranslatePipeMock,
        MockPipe(TimespanPipe),
      ],
      imports: [
        MockModule(TextFieldModule),
        MockModule(MatLegacyButtonModule),
        MockModule(MatLegacySelectModule),
        MockModule(MatLegacyFormFieldModule),
        ReactiveFormsModule,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });


  it('should have not initial value', () => {
    expect(component.fc.value).toBeNull();
  });

  describe('setting values', () => {


    it('should read value and set minutes', () => {
      component.fc.setValue({margin: 120});
      fixture.detectChanges();
      expect(component.field.form.value).toEqual({value: 2, unit: 'minutes'});
    });

    it('should convert unit and value to plain number', () => {
      component.field.form.setValue({ value: 1, unit: 'minutes' });
      fixture.detectChanges();
      expect(component.fc.value).toEqual({ margin: 60});

      component.field.form.setValue({ value: 1, unit: 'hours' });
      fixture.detectChanges();
      expect(component.fc.value).toEqual({ margin: 3600});

      component.field.form.setValue({ value: 1, unit: 'days' });
      fixture.detectChanges();
      expect(component.fc.value).toEqual({ margin: 3600 * 24});

    });

    it('should reset to undefined', () => {
      component.field.form.setValue({ value: 1, unit: 'hours' });
      fixture.detectChanges();
      expect(component.fc.value).toEqual({ margin: 3600});

      component.field.reset();
      fixture.detectChanges();
      expect(component.fc.value).toEqual({ margin: undefined});
      expect(component.field.form.value).toEqual({
        value: undefined,
        margin: undefined,
      });

    });
  });
});
