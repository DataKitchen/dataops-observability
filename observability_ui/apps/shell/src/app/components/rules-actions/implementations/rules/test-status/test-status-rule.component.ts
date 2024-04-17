import { Component } from '@angular/core';
import { AbstractRule } from '../../../abstract.rule';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RuleType } from '../../../rule.model';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { FilterFieldModule } from '@observability-ui/ui';

type Status = 'FAILED'|'WARNING'|'PASSED';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'test-status-rule',
  template: `
    <ng-container *ngIf="editMode; else displayMode">
      <div class="line">
        <span>is</span>

        <!-- <mat-form-field class="pr-3"> -->
          <!-- <mat-label>Status</mat-label> -->
          <mat-select [formControl]="form.controls.matches">
            <ng-container *ngFor="let s of status">
              <mat-option [value]="s">
                {{s | titlecase}}
              </mat-option>
            </ng-container>
          </mat-select>


          <!-- <mat-error *ngIf="form.getError('required')"> -->
            <!-- Must select a value -->
          <!-- </mat-error> -->

        <!-- </mat-form-field> -->
      </div>
    </ng-container>

    <ng-template #displayMode>
      <span>When test status is {{form.controls.matches.value | titlecase}}</span>
    </ng-template>
  `,
  styles:[`
    :host {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      align-items: center;
    }
  `],
  imports: [
    ReactiveFormsModule,
    MatSelectModule,
    CommonModule,
    // as far as `<shell-run-states>` component is used here translations
    // are loading from there. So there's no need to use `forChild` here
    TranslationModule,
    MatInputModule,
    FilterFieldModule,
  ],
  standalone: true,
})
export class TestStatusRuleComponent extends AbstractRule {

  static override label: string = 'test status';
  static override _type: RuleType = 'test_status';

  status: Status[] = [ 'FAILED', 'WARNING', 'PASSED' ];

  form = new FormGroup({
    matches: new FormControl<string | undefined>('FAILED'),
  });
}
