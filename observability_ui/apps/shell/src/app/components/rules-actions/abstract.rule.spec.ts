import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AbstractRule } from './abstract.rule';
import { Component } from '@angular/core';
import { FormControl } from '@angular/forms';

describe('abstract.rule', () => {


  @Component({
    // eslint-disable-next-line @angular-eslint/component-selector
    selector: 'test-component',
    template: `
        <h1>Test Component</h1>
    `
  })
  class TestRuleComponent extends AbstractRule {
    static override _type = 'test_rule';

    override version = 'v1';

    form = new FormControl('initial_value');
  }

  let fixture: ComponentFixture<TestRuleComponent>;
  let component: TestRuleComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TestRuleComponent ]
    }).compileComponents();

    fixture = TestBed.createComponent(TestRuleComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should return json representation of the rule', () => {
    expect(component.toJSON()).toEqual({
      rule_data: expect.objectContaining({
        conditions: expect.arrayContaining([
          { test_rule: 'initial_value' }
        ]),
      }),
      rule_schema: 'v1',
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
