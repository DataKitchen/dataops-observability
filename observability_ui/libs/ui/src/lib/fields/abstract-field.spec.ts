import { Component, Input, ViewChild } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

import { AbstractField } from './abstract-field';


describe('Abstract Field', () => {

  @Component({
    selector: 'mock-field',
    template: '<button [disabled]="disabled">{{value}}</button>',
  })
  class MockFieldComponent extends AbstractField {
    @Input() value!: string;

    override writeValue(value: string): void {
      this.value = value;
    }
  }

  @Component({
    selector: 'test-component',
    template: '<mock-field [formControl]="fc"></mock-field>'
  })
  class TestComponent {
    @ViewChild(MockFieldComponent) fieldComponent!: MockFieldComponent;
    fc = new FormControl('initial');
  }

  let fixture: ComponentFixture<TestComponent>;
  let component: TestComponent;


  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
      ],
      declarations: [
        MockFieldComponent,
        TestComponent
      ],

    });

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });


  it('should exist', () => {
    expect(component).toBeDefined();
  });

  it('should mirror initial value', () => {
    expect(component.fieldComponent.value).toEqual('initial');
  });

  it('should mirror changes to the form control', () => {
    component.fc.patchValue('new value');
    expect(component.fieldComponent.value).toEqual('new value');
  });
});
