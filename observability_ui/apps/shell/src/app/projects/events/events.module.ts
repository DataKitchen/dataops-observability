import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslationModule } from '@observability-ui/translate';
import { EventListComponent } from './event-list/event-list.component';
import { DetailsHeaderModule, FilterFieldModule, HelpLinkComponent, EmptyStateSetupComponent, TextFieldModule } from '@observability-ui/ui';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';
import { EventsRoutingModule } from './events-routing.module';
import { EventsComponent } from './events.component';
import { BatchRunsComponent } from './batch-runs/batch-runs.component';
import { ReactiveFormsModule } from '@angular/forms';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { RunsModule } from '../runs/runs.module';
import { ToolSelectorComponent } from '../integrations/tool-selector/tool-selector.component';
import { MatIconModule } from '@angular/material/icon';

@NgModule({
  imports: [
    CommonModule,
    TranslationModule.forChild({}),
    DetailsHeaderModule,
    MatTabsModule,
    EventsRoutingModule,
    ReactiveFormsModule,
    FilterFieldModule,
    FlexModule,
    MatButtonModule,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule,
    RunsModule,
    ToolSelectorComponent,
    EmptyStateSetupComponent,
    HelpLinkComponent,
    MatIconModule,
    TextFieldModule,
  ],
  declarations: [
    EventListComponent,
    EventsComponent,
    BatchRunsComponent,
  ],
  exports: [
  ],
})
export class EventsModule {
}
