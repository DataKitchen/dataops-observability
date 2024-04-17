import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { AbstractAction } from './abstract-action.directive';

describe('abstract.rule', () => {


  @Component({
    // eslint-disable-next-line @angular-eslint/component-selector
    selector: 'test-component',
    template: `
        <h1>Test Component</h1>
    `
  })
  class TestActionComponent extends AbstractAction {
    static override _type = 'test_action';

    version = 'v1';

    form = new FormControl('initial_value');
  }

  let fixture: ComponentFixture<TestActionComponent>;
  let component: TestActionComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TestActionComponent ]
    }).compileComponents();

    fixture = TestBed.createComponent(TestActionComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should return json representation of the rule', () => {
    expect(component.toJSON()).toEqual({
      action: 'test_action',
      action_args: 'initial_value',
    });
  });

  it('should parse given value', () => {
    component.parse('test_value');
    expect(component.form.getRawValue()).toEqual('test_value');
  });

  it('should update on input change', () => {

    fixture.componentRef.setInput('data', 'another_value');
    fixture.detectChanges();
    expect(component.form.getRawValue()).toEqual('another_value');
  });

});
