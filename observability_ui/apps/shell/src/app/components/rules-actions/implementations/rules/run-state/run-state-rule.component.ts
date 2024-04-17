import { AbstractRule } from '../../../abstract.rule';
import { RuleType } from '../../../rule.model';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RunAlertType, RunProcessedStatus } from '@observability-ui/core';
import { TypedFormControl } from '@datakitchen/ngx-toolkit';
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatLegacyOptionModule } from '@angular/material/legacy-core';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { TranslationModule } from '@observability-ui/translate';
import { TextFieldModule } from '@observability-ui/ui';
import { MatLegacySlideToggleModule } from '@angular/material/legacy-slide-toggle';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'shell-run-state-rule',
  template: `
    <ng-container *ngIf="editMode; else displayMode">
      <div class="line">
        <span>has a</span>

        <mat-select [formControl]="form.controls.matches">
          <mat-option [value]="Status.Failed">
            {{'runRule.' + Status.Failed | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Status.Completed">
            {{'runRule.' + Status.Completed | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Status.Running">
            {{'runRule.' + Status.Running | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Status.CompletedWithWarnings">
            {{'runRule.' + Status.CompletedWithWarnings | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Alert.MissingRun">
            {{'runRule.' + Alert.MissingRun | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Alert.LateStart">
            {{'runRule.' + Alert.LateStart | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Alert.LateEnd">
            {{'runRule.' + Alert.LateEnd | translate | lowercase}}
          </mat-option>
          <mat-option [value]="Alert.UnexpectedStatusChange">
            {{'runRule.' + Alert.UnexpectedStatusChange | translate | lowercase}}
          </mat-option>
        </mat-select>

        <ng-template #advancedOptions>
          <div class="flex-row fx-justify-flex-start">
            <div class="mr-3">{{'after' | translate | lowercase}}</div>
            <text-field class="count-input"
              [formControl]="form.controls.count"
              placeholder="0"></text-field>
            <div class="ml-3">{{'occurrencesInARow' | translate | lowercase}}</div>
          </div>

          <div class="flex-row fx-justify-flex-start">
            <div class="mr-3">{{'and' | translate | lowercase}} {{'groupedByRun' | translate | lowercase}}</div>
            <mat-slide-toggle color="primary"
              [formControl]="form.controls.group_run_name">
            </mat-slide-toggle>
          </div>

          <div class="flex-row fx-justify-flex-start mt-3">
            <div class="mr-3">{{'triggerSubsequent' | translate | lowercase}}</div>
            <mat-slide-toggle color="primary"
              [formControl]="form.controls.trigger_successive">
            </mat-slide-toggle>
          </div>

          <div class="advanced-options-link-container">
            {{'learnMoreAbout' | translate}}&nbsp;
            <a target="_blank"
              href="https://docs.datakitchen.io/article/dataops-observability-help/observability-rule-triggers/a/h3_940168387"
              class="advanced-options-link">{{'advancedOptions' | translate | lowercase}}
              <mat-icon>open_in_new</mat-icon>
            </a>
          </div>
        </ng-template>
      </div>
    </ng-container>
    <ng-template #displayMode>
      <span>When run has a&nbsp;</span>
      <span>{{'runRule.' + this.form.getRawValue().matches | translate | lowercase}}</span>
    </ng-template>
  `,
  imports: [
    ReactiveFormsModule,
    CommonModule,
    MatLegacyOptionModule,
    MatLegacySelectModule,
    TranslationModule,
    TextFieldModule,
    MatLegacySlideToggleModule,
    MatIconModule
  ],
  styleUrls: [ 'run-state-rule.component.scss' ],
  standalone: true
})
export class RunStateRuleComponent extends AbstractRule {
  static override label: string = 'run';
  static override _type: RuleType = 'run_state';

  public Status = RunProcessedStatus;
  public Alert = RunAlertType;

  advancedOptionsStatuses = [
    RunProcessedStatus.Failed,
    RunProcessedStatus.Completed,
    RunProcessedStatus.CompletedWithWarnings,
    RunProcessedStatus.Pending,
    RunAlertType.MissingRun,
    RunAlertType.LateEnd,
    RunAlertType.LateStart,
    RunAlertType.UnexpectedStatusChange
  ];

  override hasAdvancedOptions() {
    return this.advancedOptionsStatuses.includes(this.form.getRawValue().matches);
  }

  form = new FormGroup({
    matches: new FormControl<any>(RunProcessedStatus.Failed),
    count: new TypedFormControl<number>(1, [ Validators.pattern('^[0-9]+$'), Validators.required, Validators.min(1) ]),
    group_run_name: new TypedFormControl<boolean>(false),
    trigger_successive: new TypedFormControl<boolean>(true)
  });
}
