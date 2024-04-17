import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BaseComponent, ComponentType } from '@observability-ui/core';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { Subscription } from 'rxjs';
import { JourneyInstanceRulesComponent, SingleInstanceRuleControl } from './journey-instance-rules.component';
import { MockModule } from 'ng-mocks';
import { DkTooltipModule } from '@observability-ui/ui';

describe('JourneyInstanceRules', () => {
  const components: BaseComponent[] = [
    { id: '1', display_name: 'Component A', type: ComponentType.BatchPipeline } as BaseComponent,
    { id: '2', display_name: 'Component B', type: ComponentType.BatchPipeline } as BaseComponent,
    { id: '3', display_name: 'Component C', type: ComponentType.Dataset } as BaseComponent,
  ];

  let component: JourneyInstanceRulesComponent;
  let fixture: ComponentFixture<JourneyInstanceRulesComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ JourneyInstanceRulesComponent ],
      imports: [
        MockModule(DkTooltipModule),
      ],
      providers: []
    }).compileComponents();

    fixture = TestBed.createComponent(JourneyInstanceRulesComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should update the pipelines subject', () => {
    component.components = components;
    expect(component.allPipelines$.getValue()).toEqual(components.slice(0, 2));
  });

  it('should keep track of the value changes subscription', () => {
    expect(component['subscriptions'].length).toBe(1);
  });

  it('should clear the subscriptions', () => {
    const unsubscribe = jest.fn();
    component['subscriptions'] = [ { unsubscribe } as any as Subscription ];
    component.ngOnDestroy();
    expect(unsubscribe).toBeCalledTimes(1);
  });

  describe('when doing the initial setup', () => {

    describe('in all cases', () => {
      const startComponent = components[0];
      const endComponent = components[2];

      beforeEach(() => {
        component.components = components;
        component.writeValue([
          { action: 'START', batch_pipeline: startComponent.id },
          { action: 'END', batch_pipeline: endComponent.id },
        ]);
      });

      it('should initialize the form with the start rules', () => {
        const ruleControlGroup = component.form.controls['startRules'].get([ 0 ]) as SingleInstanceRuleControl;
        expect(ruleControlGroup.controls.type.value).toEqual('RUNS');
        expect(ruleControlGroup.controls.action.value).toEqual('START');
        expect(ruleControlGroup.controls.batch_pipeline.value).toEqual(startComponent.id);
      });

      it('should initialize the form with the end rules', () => {
        const ruleControlGroup = component.form.controls['endRules'].get([ 0 ]) as SingleInstanceRuleControl;
        expect(ruleControlGroup.controls.type.value).toEqual('RUNS');
        expect(ruleControlGroup.controls.action.value).toEqual('END');
        expect(ruleControlGroup.controls.batch_pipeline.value).toEqual(endComponent.id);
      });

    });

  });

  describe('when form value changes', () => {
    let onChange: (value: any) => void;

    beforeEach(() => {
      component.components = components;
      component.writeValue([
        { action: 'START', batch_pipeline: components[0].id },
        { action: 'START', batch_pipeline: components[1].id },
        { action: 'END', batch_pipeline: components[2].id },
      ]);
      onChange = jest.fn();
      component.registerOnChange(onChange);
    });

    it('should report the change to the form control and take only the first start value', () => {
      new TestScheduler().run(({ flush }) => {
        component.form.controls['startRules'].get([ 0 ])?.patchValue({ batch_pipeline: components[1].id });
        flush();
        expect(onChange).toBeCalledWith([
          { id: null, action: 'END', batch_pipeline: components[2].id, schedule: null },
          { id: null, action: 'START', batch_pipeline: components[1].id, schedule: null },
        ]);
      });
    });
  });

  describe('#addRule', () => {

    it('should show an empty rule', () => {
      expect(component.startRules.controls.length).toEqual(0);
      expect(component.endRules.controls.length).toEqual(0);
      component.addRule({ action: 'START' });
      component.addRule({ action: 'END' });
      expect(component.startRules.controls.length).toEqual(1);
      expect(component.endRules.controls.length).toEqual(1);
      component.addRule({ action: 'START' });
      component.addRule({ action: 'END' });
      expect(component.startRules.controls.length).toEqual(2);
      expect(component.endRules.controls.length).toEqual(2);
    });

  });

  describe('registerOnChange()', () => {
    it('should set the onChange callback', () => {
      const fn = jest.fn();
      component.registerOnChange(fn);
      expect(component['onChange']).toBe(fn);
    });
  });

  describe('registerOnTouched()', () => {
    it('should set the onTouched callback', () => {
      const fn = jest.fn();
      component.registerOnTouched(fn);
      expect(component['onTouched']).toBe(fn);
    });
  });

  describe('setDisabledState()', () => {
    it('should disable the form', () => {
      component.setDisabledState!(true);
      expect(component.form.disabled).toBeTruthy();
    });

    it('should enable the form', () => {
      component.setDisabledState!(false);
      expect(component.form.disabled).toBeFalsy();
    });
  });

  describe('#viewMode', () => {
    const startComponent = components[0];
    const endComponent = components[2];

    beforeEach(() => {
      component.editing = false;
      component.components = components;
      component.writeValue([
        { action: 'START', batch_pipeline: startComponent.id },
        { action: 'END', batch_pipeline: endComponent.id },
      ]);

      fixture.detectChanges();
    });

    it('should show start component', () => {
      expect(fixture.debugElement.nativeElement.textContent).toContain(startComponent.display_name);
    });

    it('should show end component', () => {
      expect(fixture.debugElement.nativeElement.textContent).toContain(endComponent.display_name);
    });
  });

  describe('#onRuleTypeChange', () => {
    it('should reset the schedule when selecting runs', () => {
      const patchValueFn = jest.fn();
      component.onRuleTypeChange({ patchValue: patchValueFn } as any, { value: 'RUNS' });
      expect(patchValueFn).toBeCalledWith({ schedule: null }, { emitEvent: false });
    });

    it('should reset the batch pipeline when choosing schedule', () => {
      const patchValueFn = jest.fn();
      component.onRuleTypeChange({ patchValue: patchValueFn } as any, { value: 'SCHEDULE' });
      expect(patchValueFn).toBeCalledWith({ batch_pipeline: null }, { emitEvent: false });
    });
  });

});
