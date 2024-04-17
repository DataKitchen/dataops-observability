import { NgModule } from '@angular/core';
import { IntegrationsComponent } from './integrations.component';
import { TranslationModule } from '@observability-ui/translate';
import { integrationsTranslations } from './integrations.translations';
import { CommonModule } from '@angular/common';
import { AlertComponent, DynamicComponentModule, FilterFieldModule, HelpLinkComponent, EmptyStateSetupComponent, TextFieldModule } from '@observability-ui/ui';
import { IntegrationsRoutingModule } from './integrations-routing.module';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { IntegrationsPanelComponent } from './integrations-panel/integrations-panel.component';
import { ReactiveFormsModule } from '@angular/forms';
import { ToolDisplayComponent } from './tools/tool-display.component';
import { MatLegacyAutocompleteModule } from '@angular/material/legacy-autocomplete';
import { MatLegacyOptionModule } from '@angular/material/legacy-core';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule } from '@angular/material/legacy-input';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { GetToolClassPipe } from './tool-selector/get-tool-class.pipe';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatLegacyPaginatorModule } from '@angular/material/legacy-paginator';
import { ToolSelectorComponent } from './tool-selector/tool-selector.component';
import { MatLegacyCardModule } from '@angular/material/legacy-card';

@NgModule({
  imports: [
    CommonModule,
    TranslationModule.forChild({
      ...integrationsTranslations
    }),
    IntegrationsRoutingModule,
    MatIconModule,
    MatButtonModule,
    TextFieldModule,
    ReactiveFormsModule,
    AlertComponent,
    DynamicComponentModule,
    MatLegacyAutocompleteModule,
    MatLegacyOptionModule,
    MatLegacyFormFieldModule,
    MatLegacyInputModule,
    ComponentIconComponent,
    GetToolClassPipe,
    MatProgressSpinnerModule,
    MatLegacyPaginatorModule,
    FilterFieldModule,
    ToolSelectorComponent,
    MatLegacyCardModule,
    EmptyStateSetupComponent,
    HelpLinkComponent
  ],
  exports: [],
  declarations: [
    IntegrationsComponent,
    IntegrationsPanelComponent,
    ToolDisplayComponent,
  ],
  providers: [],
})
export class IntegrationsModule {
}
