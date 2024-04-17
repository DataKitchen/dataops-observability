import { NgModule } from '@angular/core';
import { ComponentPanelComponent } from './component-panel.component';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatExpansionModule } from '@angular/material/expansion';
import { TranslationModule } from '@observability-ui/translate';
import { CreatedByComponent, DkTooltipModule, DynamicComponentModule, ScheduleFieldModule, TextFieldModule, TimespanFieldModule, TruncateModule } from '@observability-ui/ui';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { DeleteComponentDialogComponent } from './delete-component-dialog/delete-component-dialog.component';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { ToolSelectorComponent } from '../integrations/tool-selector/tool-selector.component';
import { GetToolClassPipe } from '../integrations/tool-selector/get-tool-class.pipe';
import { EditExpectedScheduleComponent } from '../edit-expected-schedule/edit-expected-schedule.component';
import { EditExpectedArrivalWindowComponent } from '../edit-expected-arrival-window/edit-expected-arrival-window.component';

@NgModule({
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatExpansionModule,
    RouterModule,
    TranslationModule,
    ScheduleFieldModule,
    TextFieldModule,
    TruncateModule,
    MatIconModule,
    MatButtonModule,
    FlexModule,
    MatInputModule,
    MatSelectModule,
    CreatedByComponent,
    MatProgressSpinnerModule,
    DkTooltipModule,
    TimespanFieldModule,
    MatDialogModule,
    DynamicComponentModule,
    ComponentIconComponent,
    ToolSelectorComponent,
    GetToolClassPipe,
    EditExpectedScheduleComponent,
    EditExpectedArrivalWindowComponent
  ],
  exports: [],
  declarations: [
    ComponentPanelComponent,
    DeleteComponentDialogComponent,
  ],
  providers: [],
})
export class ComponentPanelModule {
}
