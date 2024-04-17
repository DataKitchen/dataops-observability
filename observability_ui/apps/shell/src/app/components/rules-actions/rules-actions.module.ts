import { NgModule } from '@angular/core';
import { RuleDisplayComponent } from './rule-display/rule-display.component';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { AsyncPipe, KeyValuePipe, LowerCasePipe, NgForOf, NgIf, NgTemplateOutlet, TitleCasePipe } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { TemplatingLabelComponent } from './label/templating-label.component';
import { ClickConfirmDirectiveModule, DkTooltipModule, DynamicComponentModule, TextFieldModule } from '@observability-ui/ui';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacyDialog as MatDialog, MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { TemplatingAlertComponent } from './alert/templating-alert.component';
import { RunAlertType, RunProcessedStatus } from '@observability-ui/core';

@NgModule({
  imports: [
    MatCardModule,
    FlexModule,
    MatFormFieldModule,
    NgIf,
    ReactiveFormsModule,
    MatSelectModule,
    NgForOf,
    KeyValuePipe,
    DynamicComponentModule,
    MatMenuModule,
    MatIconModule,
    MatExpansionModule,
    MatProgressSpinnerModule,
    AsyncPipe,
    MatButtonModule,
    TranslationModule.forChild({
      anyComponent: 'any component in journey',
      pipeline: 'pipeline',
      for: 'for',
      inJourney: 'in journey',
      unableToSaveRule: 'The system encountered an error while saving this rule.',
      addRule: 'Add Rule',
      batchPipelineWarning: 'This rule type will only trigger for batch pipeline components.',
      when: 'When',
      advancedOptions: 'Advanced Options',
      after: 'After',
      occurrencesInARow: 'Occurrences of this status in a row',
      and: 'And',
      groupedByRun: 'Grouped by run name',
      notGroupedByRun: 'Not grouped by run name',
      triggerSubsequent: 'Trigger action for each subsequent occurrence of this status',
      notTriggerSubsequent: 'Do not trigger action for each subsequent occurrence of this status',
      runRule: {
        [RunProcessedStatus.Pending]: 'pending status',
        [RunProcessedStatus.Failed]: 'failed status',
        [RunProcessedStatus.Running]: 'running status',
        [RunProcessedStatus.CompletedWithWarnings]: 'completed with warnings status',
        [RunProcessedStatus.Completed]: 'completed status',
        [RunAlertType.MissingRun]: 'missing status',
        [RunAlertType.LateStart]: 'late start',
        [RunAlertType.LateEnd]: 'late end',
        [RunAlertType.UnexpectedStatusChange]: 'change in end status'
      },
      learnMoreAbout: 'Learn more about'
    }),
    TitleCasePipe,
    MatDialogModule,
    NgTemplateOutlet,
    DkTooltipModule,
    ClickConfirmDirectiveModule,
    TextFieldModule,
    LowerCasePipe,
  ],
  exports: [
    RuleDisplayComponent,
  ],
  declarations: [
    RuleDisplayComponent,
    TemplatingLabelComponent,
    TemplatingAlertComponent
  ],
  providers: [
    MatDialog,
  ],
})
export class RulesActionsModule {
}
