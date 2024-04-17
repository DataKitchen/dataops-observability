import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { IntegrationsComponent } from './integrations.component';
import { ToolDisplayComponent } from './tools/tool-display.component';
import { IntegrationsPanelComponent } from './integrations-panel/integrations-panel.component';

@NgModule({
  imports: [
    RouterModule.forChild([
      {
        path: '',
        component: IntegrationsComponent,
        data: {
          helpLink: 'article/dataops-observability-help/integrations'
        },
      },
      {
        path: 'guides',
        outlet: 'rightPanel',
        children: [
          {
            path: '',
            component: IntegrationsPanelComponent,
          },
          {
            path: ':tool',
            component: ToolDisplayComponent,
          },
        ],
      },
    ]),

  ],
  exports: [ RouterModule ],
})
export class IntegrationsRoutingModule {
}
