import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { InstancesListComponent } from './instances-list/instances-list.component';
import { InstanceDetailsComponent } from './instance-details/instance-details.component';
import { InstanceEventsComponent } from './instance-events/instance-events.component';
import { InstanceTimelineComponent } from './instance-timeline/instance-timeline.component';
import { InstanceRunsComponent } from './instance-runs/instance-runs.component';
import { InstanceStatusComponent } from './instance-status/instance-status.component';
import { InstanceTestsComponent } from './instance-tests/instance-tests.component';
import { TestgenIntegrationComponent } from '../testgen-integration/testgen-integration.component';

@NgModule({
  imports: [
    RouterModule.forChild([
      {
        path: '',
        component: InstancesListComponent,
        data: {
          helpLink: 'article/dataops-observability-help/instances'
        },
      },
      {
        path: ':id',
        component: InstanceDetailsComponent,
        data: {
          helpLink: 'article/dataops-observability-help/view-instance-details'
        },
        children: [
          {
            path: '',
            pathMatch: 'full',
            redirectTo: 'status',
          },
          {
            path: 'status',
            component: InstanceStatusComponent,
          },
          {
            path: 'timeline',
            component: InstanceTimelineComponent
          },
          {
            path: 'runs',
            component: InstanceRunsComponent
          },
          {
            path: 'tests',
            component: InstanceTestsComponent,
          },
          {
            path: 'events',
            component: InstanceEventsComponent,
          },
        ]
      },
      {
        path: ':id/runs/details',
        loadChildren: () => import('../runs/runs.module').then((m) => m.RunsModule),
      },
      {
        path: ':id/tests/:testId',
        outlet: 'rightPanel',
        children: [
          {
            path: 'testgen',
            component: TestgenIntegrationComponent,
          },
        ],
      },
    ])
  ],
  exports: [ RouterModule ]
})
export class InstancesRoutingModule {
}
