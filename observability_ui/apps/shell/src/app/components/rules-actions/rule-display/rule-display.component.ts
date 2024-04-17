import { ChangeDetectionStrategy, ChangeDetectorRef, Component, Inject, Input, OnInit, Optional, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { CoreComponent, Memoize, TypedFormControl } from '@datakitchen/ngx-toolkit';
import { BaseComponent, ComponentType } from '@observability-ui/core';
import { DynamicComponentOutletDirective } from '@observability-ui/ui';
import { AbstractRule } from '../abstract.rule';
import { AbstractAction } from '../abstract-action.directive';
import { DIALOG_DATA, DialogRef } from '@angular/cdk/dialog';
import { RuleStore } from '../rule.store';
import { Rule, RULES, RuleUI } from '../rule.model';
import { RULE_ACTIONS } from '../actions.model';
import { filter, map, Observable, takeUntil, tap } from 'rxjs';
import { DefaultErrorHandlerComponent } from '../../default-error-handler/default-error-handler.component';
import { MatLegacySnackBar as MatSnackBar } from '@angular/material/legacy-snack-bar';
import { FormControl, Validators } from '@angular/forms';


@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'rule-display',
  templateUrl: 'rule-display.component.html',
  styleUrls: [ 'rule-display.component.scss' ],
  // Adding this to avoid `ExpressionChangedAfterCheck` error introduced
  // while trying to read save/update button status from the actions forms
  // With this, surprisingly, we still do not need to manually trigger any
  // detection change: meaning that manually testing the ui everything works
  // fine. Although unit tests say otherwise: see comment below.
  // My understanding of this (ui still works) is that we spare a cycle of
  // detection change and this get updates for the nature of the angular forms.
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RuleDisplayComponent extends CoreComponent implements OnInit {

  @Input() components: BaseComponent[] = [];

  selectedComponent: BaseComponent|undefined;
  selecteableComponents: BaseComponent[] = [];

  selectedRule = new FormControl<typeof AbstractRule | undefined>(undefined, [ Validators.required ]);

  editing: boolean = this.data?.editing;

  @Input() rule: Rule;

  ruleUI: RuleUI;

  error: { error: { error: string; }; };

  @ViewChild('ruleDisplayer', { read: DynamicComponentOutletDirective })
  ruleDisplayerDirective!: DynamicComponentOutletDirective<AbstractRule>;

  @ViewChildren('actions', { read: DynamicComponentOutletDirective })
  actionDisplayerDirective!: QueryList<DynamicComponentOutletDirective<AbstractAction>>;

  loading$: Observable<boolean> = this.store.loading$.pipe(
    filter(({ code }) => code === 'saveOne' || code === 'updateOne' || code === 'deleteOne'),
    // filter all actions that are not relative to this particular instance
    // remember that when creating a new rule id is undefined
    // but we always create rules one by one
    filter(({ payload }) => {
      return payload[0].id === this.ruleUI.id;
    }),
    tap(({ error, status }) => {

      // when action is done
      if (!status) {
        // if there's an error show it
        if (error) {
          this.snackbar.openFromComponent(DefaultErrorHandlerComponent, {
            data: error,
            duration: 2000
          });
          this.error = error;

        } else {
          // otherwise close the dialog if it's open and
          // switch back to display mode
          this.dialog?.close();
          this.editing = false;
          this.error = null;
        }
      }
    }),
    map(({ status }) => status),
  );

  componentsForm: TypedFormControl<string> = new TypedFormControl<string>(null);

  get actionsAreInvalid(): boolean {

    if (this.actionDisplayerDirective && this.actionDisplayerDirective.toArray().length > 0) {
      return this.actionDisplayerDirective.toArray().some((actionDir) => {
        return actionDir.ref.instance.form.invalid;
      });
    }

    // defaults to true until there isn't any action
    return true;
  }

  constructor(
    private store: RuleStore,
    private snackbar: MatSnackBar,
    @Optional() private dialog: DialogRef,
    @Optional() @Inject(DIALOG_DATA) public data: {
      parentId: string,
      editing: boolean,
      components: BaseComponent[];
    },
    @Inject(RULE_ACTIONS) public actionComponents: typeof AbstractAction[],
    @Inject(RULES) public ruleComponents: typeof AbstractRule[],
    private changeDetection: ChangeDetectorRef,
  ) {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();

    this.selectedRule.valueChanges.pipe(
      tap((value) => {
        if (value) {
          this.ruleUI.conditions = [ { key: value._type, value: undefined } ];
          this.selecteableComponents = this.getSelecteableComponents(this.components, value._type);
          this.componentsForm.reset();

          // sync ui
          // from manual testing doesn't seem that the ui gets off
          // unit tests say otherwise.
          // In any case it is not a big deal to leave this here.
          this.changeDetection.markForCheck();
        }
      }),
      takeUntil(this.destroyed$),
    ).subscribe();

    this.componentsForm.valueChanges.pipe(
      tap((id) => {
        this.selectedComponent = this.components.find((component) => {
          return component.id === id;
        });
      }),
      takeUntil(this.destroyed$)
    ).subscribe();

    this.setRuleProxy();

    // when used inside the dialog data from there has precedence
    if (this.data?.components) {
      this.components = this.data.components;
    }

    // map components by id for ease of g

    this.componentsForm.patchValue(this.rule?.component as string);

    this.componentsForm.setDisabled(!this.editing);
  }

  @Memoize
  getComponent(key: string): typeof AbstractRule | undefined {
    return this.ruleComponents.find((component) => component._type === key);
  }

  @Memoize
  getActionComponent(action: string | undefined) {
    return this.actionComponents.find((component) => component._type === action);
  }

  save() {
    // check if forms are valid
    if (this.getRuleIsValid() && this.getActionsAreValid()) {
      for (const action of this.actionDisplayerDirective) {
        action.ref.instance.hydrateFromRule(this.ruleDisplayerDirective.ref.instance);
      }

      const parentId: string = this.data?.parentId || this.rule.parentId as string || '';
      const ruleId = this.rule?.id;
      const {
        rule_data,
        rule_schema
      } = this.ruleDisplayerDirective.ref.instance.toJSON();

      const action = this.actionDisplayerDirective.get(0)?.ref.instance.toJSON().action;
      const action_args = this.actionDisplayerDirective.get(0)?.ref.instance.toJSON().action_args;

      const rule = {
        action,
        action_args,
        rule_data,
      };

      if (ruleId) {
        // update existing rule
        this.store.dispatch('updateOne', {
          ...rule as Rule,
        ...(this.selectedRule.value?.showComponentSelection) && { component: this.componentsForm.value },
          id: ruleId,
        });
      } else {
        // create a new rule

        const data = {
          ...rule as Rule,
          ...(this.selectedRule.value?.showComponentSelection) && { component: this.componentsForm.value },
          rule_schema,
          parentId
        };

        this.store.dispatch('saveOne', data);
      }

    }
  }

  close() {
    this.dialog?.close();
  }

  delete(id: string) {
    this.store.dispatch('deleteOne', id);
  }

  addAction(action: typeof AbstractAction) {
    this.ruleUI.actions.push({
      component: action,
      data: undefined,
      // when an action is added default to edit mode
      editing: true,
      expanded: true,
    });
  }

  removeAction(index: number) {
    this.ruleUI.actions.splice(index);
  }

  cancel() {
    this.error = null;
    this.editing = false;
    this.componentsForm.setDisabled(!this.editing);
    // changes are not going to be applied
    // so now we reset the UI proxy to the original "rule"
    this.setRuleProxy();
    this.close();
  }

  edit() {
    this.editing = true;
    this.componentsForm.setDisabled(!this.editing);
    this.selecteableComponents = this.getSelecteableComponents(this.components, this.ruleUI.conditions[0].key);
  }

  private getRuleIsValid() {
    return this.ruleDisplayerDirective?.ref.instance.form.valid;
  }

  private getActionsAreValid() {

    if (this.actionDisplayerDirective?.toArray().length > 0) {
      return this.actionDisplayerDirective.toArray().every((actionRef) => {
        return actionRef.ref.instance.form.valid;
      });
    }

    return false;
  }

  private setRuleProxy() {

    this.ruleUI = {
      id: this.rule?.id,
      actions: [],
      conditions: [],
    };

    // for now BE allows only one rule
    if (this.rule?.action) {
      this.ruleUI.actions = [
        {
          component: this.getActionComponent(this.rule.action) as typeof AbstractAction,
          data: this.rule.action_args,
        }
      ];
    }

    if (this.rule?.rule_data.conditions) {
      this.rule.rule_data.conditions.map((value) => {

        const condition = {
          key: Object.keys(value)[0],
          value: Object.values(value)[0],
        };

        this.ruleUI.conditions.push(condition);

        this.selectedRule.setValue(this.getComponent(condition.key), {emitEvent: false});
      });
    }
  }

  private getSelecteableComponents(components: BaseComponent[], ruleType: string): BaseComponent[] {
    const batchPipelinesOnly = ![ 'test_status', 'metric_log', 'message_log' ].includes(ruleType);
    return components.filter((component) => {
      if (batchPipelinesOnly) {
        return component.type === ComponentType.BatchPipeline;
      }
      return true;
    });
  }
}
