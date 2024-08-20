import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InstancesRoutingModule } from './instances-routing.module';
import { InstancesListComponent } from './instances-list/instances-list.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { AlertComponent, DagModule, DetailsHeaderModule, DkTooltipModule, DurationModule, FilterFieldModule, GanttChartModule, GetIngrationPipe, HelpLinkComponent, EmptyStateSetupComponent, SumPipe, TableWrapperModule, TextFieldModule, TruncateModule } from '@observability-ui/ui';
import { FlexModule } from '@angular/flex-layout';
import { MatNativeDateModule } from '@angular/material/core';
import { MatLegacyTableModule as MatTableModule } from '@angular/material/legacy-table';
import { InstanceDetailsComponent } from './instance-details/instance-details.component';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';
import { TranslationModule } from '@observability-ui/translate';
import { InstanceEventsComponent } from './instance-events/instance-events.component';
import { instancesTranslation } from './instances.translation';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { InstancesStore } from '../../stores/instances/instances.store';
import { InstanceTimelineComponent } from './instance-timeline/instance-timeline.component';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { InstanceRunsComponent } from './instance-runs/instance-runs.component';
import { RunsModule } from '../runs/runs.module';
import { InstanceStatusComponent } from './instance-status/instance-status.component';
import { InstanceTestsComponent } from './instance-tests/instance-tests.component';
import { TaskTestSummaryComponent } from '../task-test-summary/task-test-summary.component';
import { InstanceRunsSummaryComponent } from './instance-runs-summary/instance-runs-summary.component';
import { SummaryComponent } from '../../components/summary/summary.component';
import { SummaryItemComponent } from '../../components/summary-item/summary-item.component';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { ToolSelectorComponent } from '../integrations/tool-selector/tool-selector.component';
import { InstanceAlertsComponent } from './instance-alerts/instance-alerts.component';
import { JourneyDagLegendComponent } from '../journey-dag-legend/journey-dag-legend.component';

@NgModule({
  providers: [
    InstancesStore
  ],
  declarations: [
    InstancesListComponent,
    InstanceDetailsComponent,
    InstanceEventsComponent,
    InstanceTimelineComponent,
    InstanceRunsComponent,
    InstanceStatusComponent,
    InstanceTestsComponent,
    InstanceRunsSummaryComponent
  ],
  imports: [
    CommonModule,
    InstancesRoutingModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatDatepickerModule,
    FilterFieldModule,
    TableWrapperModule,
    TextFieldModule,
    FlexModule,
    DurationModule,
    MatNativeDateModule,
    MatTableModule,
    DetailsHeaderModule,
    MatTabsModule,
    TranslationModule.forChild(instancesTranslation),
    MatIconModule,
    MatButtonModule,
    DkTooltipModule,
    TruncateModule,
    GanttChartModule,
    MatCardModule,
    MatProgressSpinnerModule,
    RunsModule,
    DagModule,
    TaskTestSummaryComponent,
    AlertComponent,
    ComponentIconComponent,
    SummaryComponent,
    SummaryItemComponent,
    ToolSelectorComponent,
    GetIngrationPipe,
    InstanceAlertsComponent,
    JourneyDagLegendComponent,
    EmptyStateSetupComponent,
    HelpLinkComponent,
    SumPipe,
  ]
})
export class InstancesModule {
}
