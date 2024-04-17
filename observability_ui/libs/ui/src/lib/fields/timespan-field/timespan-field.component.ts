import { Component, Input, OnInit, Optional, Self } from '@angular/core';
import { AbstractField } from '../abstract-field';
import { NgControl, Validators } from '@angular/forms';
import { Schedule } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { tap } from 'rxjs';

type Model = {
  value: number;
  unit: 'minutes' | 'hours' | 'days' ;
};

@Component({
  selector: 'timespan-field',
  templateUrl: './timespan-field.component.html',
  styleUrls: [ 'timespan-field.component.scss' ]
})
export class TimespanFieldComponent extends AbstractField<Schedule> implements OnInit {
  @Input() label!: string;

  form = new TypedFormGroup<Model>({
    value: new TypedFormControl<number>(undefined, [ Validators.pattern('^[0-9]+$') ]),
    unit: new TypedFormControl<'minutes' | 'hours' | 'days'>(),
  });

  constructor(
    @Self() @Optional() override ngControl?: NgControl,
  ) {
    super(ngControl);
    this.form.valueChanges.pipe(
      tap(({value, unit}) => {

        this.control.patchValue({
          ...this.control.value,
          margin: this.getMargin({ value, unit: unit ?? 'minutes' }),
        }, {emitEvent: false});

      }),
      takeUntilDestroyed(),
    ).subscribe();
  }

  override writeValue(value: Schedule) {
    this.form.patchValue(this.getUnitAndValueFromMargin(value?.margin), { emitEvent: false });
  }

  private getUnitAndValueFromMargin(margin: number): {
    unit: 'minutes' | 'days' | 'hours' | undefined;
    value: number | undefined;
  } {


    if (margin === undefined || margin === null) {
      return {
        unit: undefined,
        value: undefined,
      };
    }


    if (Number.isInteger(margin / 86400)) {
      return { unit: 'days', value: margin / 86400 };
    } else if (Number.isInteger(margin / 3600)) {
      return { unit: 'hours', value: margin / 3600 };
    }

    return { unit: 'minutes', value: margin / 60 };
  }

  private getMargin({ value, unit }: Model) {

    if (!value || !unit) {
      return undefined;
    }

    if ( unit === 'hours') {
      return value * 60 * 60;
    } else if (unit === 'days') {
      return value * 24 * 60 * 60;
    } else {
      return value * 60;
    }
  }

  reset() {
    this.form.reset();
  }
}
