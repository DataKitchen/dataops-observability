import { NgModule } from '@angular/core';
import { RunsRoutingModule } from './runs-routing.module';
import { MatLegacyTableModule as MatTableModule } from '@angular/material/legacy-table';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { RunDetailsComponent } from './run-details/run-details.component';
import { RunEventsComponent } from './run-events/run-events.component';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { DagModule, DetailsHeaderModule, DkTooltipModule, DurationModule, EntityModule, FilterFieldModule, GanttChartModule, GetIngrationPipe, IsTodayPipe, MetadataViewerModule, ParseDatePipe, TableWrapperModule, TextFieldModule, TruncateModule } from '@observability-ui/ui';
import { RunTimelineComponent } from './run-timeline/run-timeline.component';
import { runsTranslation } from './runs.translation';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { FlexModule } from '@angular/flex-layout';
import { RunDagComponent } from './run-dag/run-dag.component';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { RunsTableComponent } from './runs-table/runs-table.component';
import { EventsTableComponent } from './events-table/events-table.component';
import { RunStatesComponent } from './runs-table/run-states/run-states.component';
import { TaskTestSummaryComponent } from '../task-test-summary/task-test-summary.component';
import { RunTimeComponent } from './runs-table/run-time/run-time.component';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { RunTestsComponent } from './run-tests/run-tests.component';
import { SummaryComponent } from '../../components/summary/summary.component';
import { SummaryItemComponent } from '../../components/summary-item/summary-item.component';

@NgModule({
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatButtonModule,
    RunsRoutingModule,
    EntityModule,
    DagModule,
    TranslationModule.forChild(runsTranslation),
    DkTooltipModule,
    TruncateModule,
    GanttChartModule,
    TextFieldModule,
    ReactiveFormsModule,
    MatNativeDateModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatInputModule,
    TableWrapperModule,
    FlexModule,
    MetadataViewerModule,
    FilterFieldModule,
    MatCardModule,
    DetailsHeaderModule,
    DurationModule,
    TaskTestSummaryComponent,
    ParseDatePipe,
    ComponentIconComponent,
    IsTodayPipe,
    GetIngrationPipe,
    SummaryComponent,
    SummaryItemComponent,
  ],
  declarations: [
    RunDagComponent,
    RunDetailsComponent,
    RunEventsComponent,
    RunTimelineComponent,
    RunsTableComponent,
    EventsTableComponent,
    RunStatesComponent,
    RunTimeComponent,
    RunTestsComponent,
  ],
  exports: [
    RunsTableComponent,
    EventsTableComponent,
    RunStatesComponent,
  ],
})
export class RunsModule {
}
