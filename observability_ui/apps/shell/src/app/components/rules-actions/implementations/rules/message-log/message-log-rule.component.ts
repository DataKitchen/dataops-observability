import { Component } from '@angular/core';
import { AbstractRule } from '../../../abstract.rule';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Rule, RuleType } from '../../../rule.model';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { FilterFieldModule } from '@observability-ui/ui';

type Level = 'ERROR' | 'WARNING' | 'INFO';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'message-log-rule',
  template: `
    <ng-container *ngIf="editMode; else displayMode">
      <div class="line">
        <span>level =</span>

      <!--      <filter-field class="pr-3" label="Level" allSelectedLabel="any level"-->
      <!--                    [formControl]="form.controls.level" multiple="true">-->
      <!--        <ng-container *ngFor="let level of levels">-->
      <!--            <filter-field-option [value]="level">{{level}}</filter-field-option>-->
      <!--        </ng-container>-->
      <!--      </filter-field>-->

      <!-- <mat-form-field class="pr-3"> -->
        <!-- <mat-label>{{ form.controls.level.value?.length > 0 ? 'Level' : 'Any Level'}}</mat-label> -->
        <mat-select [formControl]="form.controls.level" placeholder="any" multiple>
          <ng-container *ngFor="let level of levels">
            <mat-option [value]="level">
              {{level | translate}}
            </mat-option>
          </ng-container>
        </mat-select>


        <!-- <mat-error *ngIf="form.getError('required')"> -->
          <!-- Must select a value -->
        <!-- </mat-error> -->

      <!-- </mat-form-field> -->

        <span>and message contains</span>

      <!-- <mat-form-field class="pr-3"> -->
        <!-- <mat-label>Pattern</mat-label> -->
        <input matInput [formControl]="form.controls.matches">

        <!-- <mat-hint></mat-hint> -->
        <!-- <mat-error *ngIf="form.getError('required')"> -->
          <!-- This field is required -->
        <!-- </mat-error> -->
      <!-- </mat-form-field> -->
      </div>
    </ng-container>

    <ng-template #displayMode>

      <div class="fx-flex-wrap">
        When log level matches
        <ng-container *ngIf="form.controls.level.value?.length > 0; else anythingTpl">
          <ng-container *ngFor="let v of form.controls.level.value; last as last">
            <code class="pr-2">{{v|translate}}</code><span *ngIf="!last" class="pr-2">or</span>
          </ng-container>
        </ng-container>
        <ng-template #anythingTpl><code>any</code></ng-template>
        and message contains <code>{{form.controls.matches.value}}</code>

      </div>

    </ng-template>
  `,
  styles: [ `
    :host {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      align-items: center;
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
    FilterFieldModule,
  ],
  standalone: true,
})
export class MessageLogRuleComponent extends AbstractRule {

  static override label: string = 'log matches';
  static override _type: RuleType = 'message_log';

  levels: Level[] = [ 'ERROR', 'WARNING', 'INFO' ];

  form = new FormGroup({
    level: new FormControl<string[]|undefined>(undefined),
    matches: new FormControl<string | undefined>(undefined),
  });

  override toJSON(): Pick<Rule, 'rule_data' | 'rule_schema'> {

    const level = this.form.controls.level.value ?? [];

    const formData = {
      ...this.form.value,
      level,
    };

    return {
      rule_data: {
        when: 'all',
        conditions: [ {
          [this.type]: formData
        } ]
      },
      rule_schema: this.version,
    };
  }
}
