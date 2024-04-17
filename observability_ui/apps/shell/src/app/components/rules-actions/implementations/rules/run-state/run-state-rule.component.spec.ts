

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RunStateRuleComponent } from './run-state-rule.component';

describe('run-state-rule', () => {

  let component: RunStateRuleComponent;
  let fixture: ComponentFixture<RunStateRuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ RunStateRuleComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(RunStateRuleComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });



});
