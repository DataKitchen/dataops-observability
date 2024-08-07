import { NgModule } from '@angular/core';
import { CoreModule } from '@observability-ui/core';
import { CommonModule } from '@angular/common';
import { JourneysListComponent } from './journeys-list/journeys-list.component';
import { JourneysRoutingModule } from './journeys-routing.module';
import { JourneysStore } from './journeys.store';
import { CreatedByComponent, DagModule, DetailsHeaderModule, DkTooltipModule, FilterFieldModule, HelpLinkComponent, MatCardEditComponent, ScheduleFieldModule, EmptyStateSetupComponent, TextFieldModule, TruncateModule } from '@observability-ui/ui';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { AddJourneyDialogComponent } from './add-journey-dialog/add-journey-dialog.component';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { JourneyDetailsComponent } from './journey-details/journey-details.component';
import { JourneySettingsComponent } from './journey-settings/journey-settings.component';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';
import { TranslationModule } from '@observability-ui/translate';
import { JourneyRulesComponent } from './journey-rules/journey-rules.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { RulesActionsModule } from '../../components/rules-actions/rules-actions.module';
import { RULES } from '../../components/rules-actions/rule.model';
import { TaskStatusRuleComponent } from '../../components/rules-actions/implementations/rules/task-status/task-status-rule.component';
import { MatRippleModule } from '@angular/material/core';
import { OverlayModule } from '@angular/cdk/overlay';
import { journeysTranslations } from './journeys.translation';
import { JourneyRelationshipsComponent } from './journey-relationships/journey-relationships.component';
import { MetricLogRuleComponent } from '../../components/rules-actions/implementations/rules/metric-log/metric-log-rule.component';
import { MessageLogRuleComponent } from '../../components/rules-actions/implementations/rules/message-log/message-log-rule.component';
import { TestStatusRuleComponent } from '../../components/rules-actions/implementations/rules/test-status/test-status-rule.component';
import { JourneyInstanceRulesComponent } from './journey-instance-rules/journey-instance-rules.component';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { InstanceHasAlertRuleComponent } from '../../components/rules-actions/implementations/rules/instance-has-alert/instance-has-alert-rule.component';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { RunStateRuleComponent } from '../../components/rules-actions/implementations/rules/run-state/run-state-rule.component';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatRadioModule } from '@angular/material/radio';
import { MatLegacyCheckboxModule } from '@angular/material/legacy-checkbox';
import { JourneyDagLegendComponent } from '../journey-dag-legend/journey-dag-legend.component';

@NgModule({
  providers: [
    JourneysStore,
    {
      provide: RULES,
      useValue: [
        TaskStatusRuleComponent,
        RunStateRuleComponent,
        MetricLogRuleComponent,
        MessageLogRuleComponent,
        TestStatusRuleComponent,
        InstanceHasAlertRuleComponent,
        // ExampleRuleComponent,
      ],
    },
  ],
  declarations: [
    JourneysListComponent,
    AddJourneyDialogComponent,
    JourneyDetailsComponent,
    JourneySettingsComponent,
    JourneyRelationshipsComponent,
    JourneyRulesComponent,
    JourneyInstanceRulesComponent,
  ],
  imports: [
    CoreModule,
    CommonModule,
    DagModule,
    JourneysRoutingModule,
    TextFieldModule,
    TranslationModule.forChild(journeysTranslations),
    ReactiveFormsModule,
    MatPaginatorModule,
    FlexModule,
    MatProgressSpinnerModule,
    MatCardModule,
    FilterFieldModule,
    MatIconModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    DetailsHeaderModule,
    MatTabsModule,
    TranslationModule,
    DkTooltipModule,
    MatExpansionModule,
    RulesActionsModule,
    MatRippleModule,
    OverlayModule,
    TruncateModule,
    MatSelectModule,
    MatDialogModule,
    CreatedByComponent,
    MatMenuModule,
    ScheduleFieldModule,
    MatCardEditComponent,
    ComponentIconComponent,
    MatRadioModule,
    HelpLinkComponent,
    EmptyStateSetupComponent,
    MatLegacyCheckboxModule,
    JourneyDagLegendComponent,
  ],
})
export class JourneysModule {
}
