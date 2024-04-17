import { Component } from '@angular/core';
import { AbstractRule } from '../../../abstract.rule';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RuleType } from '../../../rule.model';
import { TranslationModule } from '@observability-ui/translate';
import { RunsModule } from '../../../../../projects/runs/runs.module';
import { Run, RunProcessedStatus } from '@observability-ui/core';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'task-status-rule',
  template: `
    <ng-container *ngIf="editMode; else displayMode">
      <!-- <mat-form-field> -->
        <!-- <mat-label>Task Status</mat-label> -->
      <div class="line">
        <span>is</span>

        <mat-select [formControl]="form.controls.matches">
          <mat-option [value]="Status.Failed">
            {{'runStatus.' + Status.Failed | translate}}
          </mat-option>
          <mat-option [value]="Status.Completed">
            {{'runStatus.' + Status.Completed | translate}}
          </mat-option>
          <mat-option [value]="Status.Running">
            {{'runStatus.' + Status.Running | translate}}
          </mat-option>
          <mat-option [value]="Status.CompletedWithWarnings">
            {{'runStatus.' + Status.CompletedWithWarnings | translate}}
          </mat-option>
        </mat-select>
      </div>
        <!-- <mat-error *ngIf="form.getError('required')">
          Must select a value
        </mat-error> -->
      <!-- </mat-form-field> -->
    </ng-container>

    <ng-template #displayMode>
      <span>When task status is</span>
      <shell-run-states [run]="run"></shell-run-states>
    </ng-template>
  `,
  styles:[ `
    :host {
      display: flex;
      flex-direction: row;
    }

    shell-run-states {
      padding-left: 4px;
    }
  ` ],
  imports: [
    ReactiveFormsModule,
    MatSelectModule,
    CommonModule,
    RunsModule,
    // as far as `<shell-run-states>` component is used here translations
    // are loading from there. So there's no need to use `forChild` here
    TranslationModule,
  ],
  standalone: true,
})
export class TaskStatusRuleComponent extends AbstractRule {

  static override label: string = 'task status';
  static override _type: RuleType = 'task_status';
  static override alert: string = 'This rule type will only trigger for batch pipeline components.';
  static override alertIcon: string = 'info_circle';

  Status = RunProcessedStatus;

  get run() {
    return {
      status: this.form.getRawValue().matches,
    } as Run;
  }

  form = new FormGroup({
    matches: new FormControl<RunProcessedStatus|null>(RunProcessedStatus.Failed)
  });
}
