import { Component, Input, OnDestroy, OnInit, Optional, Self } from '@angular/core';
import { ControlValueAccessor, FormControl, FormGroup, NgControl, UntypedFormArray, UntypedFormGroup } from '@angular/forms';
import { BaseComponent, ComponentType, JourneyInstanceRule } from '@observability-ui/core';
import { omit, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { BehaviorSubject, filter, noop, Subscription } from 'rxjs';

export type SingleInstanceRuleControl = FormGroup<{
  id: FormControl<string>;
  type: FormControl<'RUNS'>;
  action: FormControl<'START' | 'END' | null>;
  batch_pipeline: FormControl<string | null>;
  schedule: FormControl<{ schedule: string; timezone?: string | undefined; } | null>;
}>;

@Component({
  selector: 'shell-journey-instance-rules',
  templateUrl: './journey-instance-rules.component.html',
  styleUrls: [ './journey-instance-rules.component.scss' ]
})
export class JourneyInstanceRulesComponent implements ControlValueAccessor, OnInit, OnDestroy {
  @Input() editing: boolean = false;
  @Input() isPayload: boolean = false;

  @Input() set components(value: BaseComponent[]) {
    if (value !== null && value !== undefined) {
      for (const c of value) {
        this.componentsMap[c.id] = c;
      }
      this.allPipelines$.next(value.filter(component => component.type === ComponentType.BatchPipeline));
    }
  }

  componentsMap: { [id: string]: BaseComponent } = {};

  startRules = new UntypedFormArray([]);
  endRules = new UntypedFormArray([]);

  form = new UntypedFormGroup({
    startRules: this.startRules,
    endRules: this.endRules,
    trackSeparately: new FormControl<boolean>(false)
  });

  allPipelines$ = new BehaviorSubject<BaseComponent[]>([]);

  private subscriptions: Subscription[] = [];

  constructor(@Self() @Optional() protected ngControl?: NgControl) {
    if (ngControl) {
      ngControl.valueAccessor = this;
    }
  }

  protected onChange: (value: JourneyInstanceRule[]) => void = noop;

  protected onTouched: () => void = noop;

  ngOnInit(): void {
    const sub = this.form.valueChanges.pipe(
      filter(() => this.form.valid)
    ).subscribe(({ startRules, endRules }) => {
      // recollect all rules without (implicit) `type` to set then on parent form
      this.reconcileValues(startRules, endRules);
    });

    this.subscriptions.push(sub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(s => s.unsubscribe());
  }

  writeValue(value: JourneyInstanceRule[]): void {
    this.setFormValue(value);
  }

  registerOnChange(fn: (value: JourneyInstanceRule[]) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState?(isDisabled: boolean): void {
    if (isDisabled) {
      return this.form.disable();
    }
    return this.form.enable();
  }

  private setFormValue(rules: JourneyInstanceRule[]): void {    // reset all previous values
    this.startRules.clear({ emitEvent: false });
    this.endRules.clear({ emitEvent: false });

    if (this.isPayload && rules.length > 0) {
      this.form.patchValue({ trackSeparately: true });
    }

    for (const rule of rules) {
      if (rule.schedule) {
        rule.schedule = {
          ...rule.schedule,
          schedule: (rule.schedule as any).expression,
        };
      }

      this.addRule(rule);
    }

    if (!this.isPayload && this.startRules.controls.length === 0) {
      this.addRule({
        action: 'START',
      }, 'DEFAULT');
    }

    // this is only meant to trigger a value change
    // because in `addRule` we not emitting values to avoid a change for each item added
    this.form.enable();
  }

  addRule(rule: JourneyInstanceRule, type: 'SCHEDULE' | 'RUNS' | 'DEFAULT' = null) {
    const fg = new TypedFormGroup({
      id: new TypedFormControl<string>(rule.id),
      type: new TypedFormControl<'SCHEDULE' | 'RUNS' | 'DEFAULT'>(type ? type : rule.schedule ? 'SCHEDULE' : 'RUNS'),
      action: new TypedFormControl(this.isPayload ? 'END_PAYLOAD' : rule.action),
      batch_pipeline: new TypedFormControl(rule.batch_pipeline as string),
      schedule: new TypedFormControl(rule.schedule),
    });

    const sub = fg.valueChanges.subscribe((value) => {
      this.onRuleTypeChange(fg, { value: value.type });
    });

    this.subscriptions.push(sub);

    if (rule.action === 'START') {
      this.startRules.push(fg, { emitEvent: false });
    }

    if (rule.action === 'END') {
      this.endRules.push(fg, { emitEvent: false });
    }

    if (rule.action === 'END_PAYLOAD') {
      this.endRules.push(fg, { emitEvent: false });
    }
  }

  private reconcileValues(startRules: any, endRules: any) {
    const rules = [
      ...endRules!.map((rule: JourneyInstanceRule) => omit(rule, [ 'type' ]))
    ];

    if (!this.isPayload && startRules && startRules[0]?.type !== 'DEFAULT') {
      rules.push(omit(startRules[0], [ 'type' ]));
    }

    this.onChange(rules);
  }

  onRuleTypeChange(form: FormGroup, event: { value: 'RUNS' | 'SCHEDULE' | 'DEFAULT' }) {
    if (event.value === 'RUNS') {
      form.patchValue({
        schedule: null
      }, { emitEvent: false });
    } else if (event.value === 'SCHEDULE') {
      form.patchValue({
        batch_pipeline: null
      }, { emitEvent: false });
    } else {
      form.patchValue({
        batch_pipeline: null,
        schedule: null
      }, { emitEvent: false });
    }
  }

  deleteRule(array: UntypedFormArray, index: number) {
    array.removeAt(index);
  }
}
