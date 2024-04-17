import { ComponentsListComponent } from './components-list/components-list.component';
import { AddComponentDialogComponent } from './add-component-dialog/add-component-dialog.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { CoreModule } from '@observability-ui/core';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { ComponentsRoutingModule } from './components-routing.module';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { CreatedByComponent, DkTooltipModule, DynamicComponentModule, FilterFieldModule, HelpLinkComponent, SelectedActionsComponent, EmptyStateSetupComponent, TextFieldModule, TruncateModule } from '@observability-ui/ui';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';
import { TranslationModule } from '@observability-ui/translate';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { MatLegacyInputModule } from '@angular/material/legacy-input';
import { ComponentIconComponent } from './component-icon/component-icon.component';
import { ToolSelectorComponent } from '../integrations/tool-selector/tool-selector.component';
import { GetToolClassPipe } from '../integrations/tool-selector/get-tool-class.pipe';
import { MatLegacyCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacyDialogModule } from '@angular/material/legacy-dialog';
import { NgModule } from '@angular/core';
import { LayoutModule } from '@angular/cdk/layout';
import { MatDividerModule } from '@angular/material/divider';

@NgModule({
  declarations: [
    AddComponentDialogComponent,
    ComponentsListComponent
  ],
  providers: [],
  imports: [
    CoreModule,
    CommonModule,
    ReactiveFormsModule,
    MatLegacyDialogModule,
    MatIconModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatButtonModule,
    TextFieldModule,
    TranslationModule,
    ComponentsRoutingModule,
    TruncateModule,
    DkTooltipModule,
    FlexModule,
    MatSelectModule,
    MatMenuModule,
    DynamicComponentModule,
    MatPaginatorModule,
    FilterFieldModule,
    CreatedByComponent,
    MatLegacyInputModule,
    ComponentIconComponent,
    ToolSelectorComponent,
    GetToolClassPipe,
    MatLegacyCheckboxModule,
    SelectedActionsComponent,
    EmptyStateSetupComponent,
    LayoutModule,
    MatDividerModule,
    HelpLinkComponent
  ]
})
export class ComponentsModule {
}
