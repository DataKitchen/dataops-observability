import { Component } from '@angular/core';
import { AbstractRule } from '../../../abstract.rule';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RuleType } from '../../../rule.model';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';

type Operator =
  'exact'
  // | 'not_equal'
  | 'lt'
  | 'lte'
  | 'gt'
  | 'gte';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'metric-log-rule',
  template: `
    <ng-container *ngIf="editMode; else displayMode">
      <!-- <mat-form-field class="pr-3"> -->
        <!-- <mat-label>Matches</mat-label> -->
      <div class="line">
        <span>key =</span>
        <input matInput
          [formControl]="form.controls.key"
          autofocus>
        <!-- <mat-hint></mat-hint> -->
        <!-- <mat-error *ngIf="form.getError('required')"> -->
          <!-- This field is required -->
        <!-- </mat-error> -->
      <!-- </mat-form-field> -->

        <span>and value</span>

      <!-- <mat-form-field class="pr-3"> -->
        <!-- <mat-label>Operator</mat-label> -->
        <mat-select [formControl]="form.controls.operator">
          <ng-container *ngFor="let operator of operators">
            <mat-option [value]="operator">
              {{operator | translate}}
            </mat-option>
          </ng-container>
        </mat-select>
        <!-- <mat-error *ngIf="form.getError('required')"> -->
          <!-- Must select a value -->
        <!-- </mat-error> -->
      <!-- </mat-form-field> -->

      <!-- <mat-form-field class="pr-3"> -->
        <!-- <mat-label>Value</mat-label> -->
        <input matInput [formControl]="form.controls.static_value"
          type="number">
        <!-- <mat-hint></mat-hint> -->
        <!-- <mat-error *ngIf="form.getError('required')"> -->
          <!-- This field is required -->
        <!-- </mat-error> -->
      <!-- </mat-form-field> -->
      </div>
    </ng-container>


    <ng-template #displayMode>
      <div class="fx-flex-wrap">When metric log matches <code>"{{form.controls.key.value}}"</code>
        and value {{form.controls.operator.value | translate}} <code>"{{form.controls.static_value.value}}"</code></div>

    </ng-template>
  `,
  styles: [ `
    /* :host {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      align-items: center;
    } */
    :host {
      display: flex;
      flex-direction: row;
    }



  ` ],
  imports: [
    ReactiveFormsModule,
    MatSelectModule,
    CommonModule,
    // as far as `<shell-run-states>` component is used here translations
    // are loading from there. So there's no need to use `forChild` here
    TranslationModule,
    MatInputModule,
  ],
  standalone: true,
})
export class MetricLogRuleComponent extends AbstractRule {

  static override label: string = 'metric matches';
  static override _type: RuleType = 'metric_log';

  operators: Operator[] = [ 'exact', 'lt', 'lte', 'gt', 'gte' ];

  form = new FormGroup({
    key: new FormControl<string | undefined>(undefined, [ Validators.required ]),
    operator: new FormControl<Operator | undefined>(undefined, [ Validators.required ]),
    static_value: new FormControl<number | undefined>(undefined, [ Validators.required ]),
  });
}
