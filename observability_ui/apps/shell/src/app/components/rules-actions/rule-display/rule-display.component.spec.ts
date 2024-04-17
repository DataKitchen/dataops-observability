import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RuleDisplayComponent } from './rule-display.component';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { DkTooltipModule, DynamicComponentModule } from '@observability-ui/ui';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { RuleStore } from '../rule.store';
import { RULES } from '../rule.model';
import { ExampleRuleComponent } from '../implementations/rules/example/example-rule.component';
import { RULE_ACTIONS } from '../actions.model';
import { ExampleActionComponent } from '../implementations/actions/example/example-action.component';
import { DIALOG_DATA, DialogRef } from '@angular/cdk/dialog';
import { MatLegacySnackBarModule as MatSnackBarModule } from '@angular/material/legacy-snack-bar';
import { BehaviorSubject } from 'rxjs';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { ReactiveFormsModule } from '@angular/forms';
import { MatExpansionModule } from '@angular/material/expansion';
import { TemplatingLabelComponent } from '../label/templating-label.component';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { TemplatingAlertComponent } from '../alert/templating-alert.component';

describe('rule-display', () => {

  let component: RuleDisplayComponent;
  let fixture: ComponentFixture<RuleDisplayComponent>;
  let dialog: Mocked<DialogRef>;
  let store: Mocked<RuleStore>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatCardModule,
        MatFormFieldModule,
        MatSelectModule,
        DynamicComponentModule,
        NoopAnimationsModule,
        MatSnackBarModule,
        MatProgressSpinnerModule,
        MatIconModule,
        MatMenuModule,
        ReactiveFormsModule,
        MatExpansionModule,
        MatDialogModule,
        DkTooltipModule,
      ],
      declarations: [
        RuleDisplayComponent,
        TemplatingLabelComponent,
        TemplatingAlertComponent,
        TranslatePipeMock,
      ],
      providers: [
        MockProvider(RuleStore, class {
          loading$ = new BehaviorSubject({
            code: 'saveOne', status: false,
          });
        }),
        {
          provide: RULES,
          useValue: [ ExampleRuleComponent ],
        },
        {
          provide: RULE_ACTIONS,
          useValue: [ ExampleActionComponent ]
        },
        MockProvider(DialogRef),
        {
          provide: DIALOG_DATA,
          useValue: {
            // when saving a new rule pipeline id comes from `data` i.e.: the dialog
            parentId: 'pipeline_id'
          },
        },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RuleDisplayComponent);
    component = fixture.componentInstance;

    dialog = TestBed.inject(DialogRef) as Mocked<DialogRef>;
    store = TestBed.inject(RuleStore) as Mocked<RuleStore>;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('create a new rule', () => {

    beforeEach(() => {

      // trigger ngOnInit
      fixture.detectChanges();
      component.editing = true;
      component.selectedRule.setValue(ExampleRuleComponent);

      // detect component in edit mode
      fixture.detectChanges();
    });

    it('should be able to select a rule ', () => {
      expect(component.ruleDisplayerDirective).toBeTruthy();
    });

    describe('save', () => {

      beforeEach(() => {

        // add an action
        component.addAction(ExampleActionComponent);
        fixture.detectChanges();
      });

      it('should save a new rule', () => {
        // make rule and actions valid
        component.ruleDisplayerDirective.ref.instance.form.setValue('Geronimo');
        component.actionDisplayerDirective.get(0)?.ref.instance.form.setValue('fearless');

        // @ts-ignore
        component.actionDisplayerDirective.get(0).ref.instance.hydrateFromRule = jest.fn();
        component.save();

        expect(component.actionDisplayerDirective.get(0)?.ref.instance.hydrateFromRule).toBeCalledWith(component.ruleDisplayerDirective.ref.instance);
        expect(store.dispatch).toHaveBeenCalledWith('saveOne', expect.objectContaining({
          action: ExampleActionComponent._type,
          action_args: 'fearless',
          rule_data: expect.objectContaining({
            conditions: [ { example_rule: 'Geronimo' } ]
          }),
          rule_schema: expect.anything(),
        }));
      });

    });

  });

  describe('display a rule', () => {

    const ruleValue = 'Geronimo';
    const ruleLabel = `My name is: ${ ruleValue }`;

    const actionLabel = 'fearless';

    beforeEach(() => {

      // since this is set after component has been created
      // form's value change kicks in after `ngOnChange` resetting
      // the value set in condition.
      // this won't happen in real use case.
      fixture.componentRef.setInput('rule', {
        'id': '9657d8824b904bf4889625e68151099e',
        'rule_schema': 'simple_v1',
        'rule_data': {
          'when': 'all',
          'conditions': [
            { [ExampleRuleComponent._type]: ruleValue }
          ]
        },
        'action': ExampleActionComponent._type,
        'action_args': 'fearless'
      });

      fixture.detectChanges();

      // // so we need to set again the rule's value
      component.ruleDisplayerDirective.ref.instance.form.setValue(ruleValue);

      fixture.detectChanges();
    });

    it('should show rule', () => {
      expect(fixture.debugElement.nativeElement.textContent).toContain(ruleLabel);
    });

    it('should show action', () => {
      expect(fixture.debugElement.nativeElement.textContent).toContain(actionLabel);
    });

    it('should be able to edit rule', () => {
      component.editing = true;

      component.ruleDisplayerDirective.ref.instance.form.setValue('Geronimo edit');
      component.actionDisplayerDirective.get(0)?.ref.instance.form.setValue('fearless edit');

      component.save();

      expect(store.dispatch).toHaveBeenCalledWith('updateOne', {
        action: 'EXAMPLE_ACTION',
        action_args: 'fearless edit',
        id: '9657d8824b904bf4889625e68151099e',
        rule_data: {
          'conditions': [ { 'example_rule': 'Geronimo edit' } ],
          'when': 'all'
        },
      });

    });
  });

  describe('#close', () => {
    it('should close dialog', () => {
      component.close();
      expect(dialog.close).toHaveBeenCalled();
    });
  });

  describe('#delete', () => {
    it('should dispatch event', () => {
      component.delete('id');

      expect(store.dispatch).toHaveBeenCalled();
    });
  });

});
