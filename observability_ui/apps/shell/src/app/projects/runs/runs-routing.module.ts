import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { RunDagComponent } from './run-dag/run-dag.component';
import { RunDetailsComponent } from './run-details/run-details.component';
import { RunEventsComponent } from './run-events/run-events.component';
import { RunTimelineComponent } from './run-timeline/run-timeline.component';
import { RunTestsComponent } from './run-tests/run-tests.component';
import { TestgenIntegrationComponent } from '../testgen-integration/testgen-integration.component';

@NgModule({
  imports: [
    RouterModule.forChild([
      {
        path: ':runId',
        component: RunDetailsComponent,
        data: {
          helpLink: 'article/dataops-observability-help/view-run-details'
        },
        children: [
          {
            path: '',
            pathMatch: 'full',
            redirectTo: 'graph',
          },
          {
            path: 'graph',
            component: RunDagComponent,
          },
          {
            path: 'events',
            component: RunEventsComponent,
          },
          {
            path: 'timeline',
            component: RunTimelineComponent
          },
          {
            path: 'tests',
            component: RunTestsComponent
          }
        ]
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
export class RunsRoutingModule {}
