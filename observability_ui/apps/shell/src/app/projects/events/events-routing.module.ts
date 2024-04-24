import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { EventsComponent } from './events.component';
import { EventListComponent } from './event-list/event-list.component';
import { BatchRunsComponent } from './batch-runs/batch-runs.component';

@NgModule({
  imports: [
    RouterModule.forChild([
      {
        path: '',
        component: EventsComponent,
        data: {
          helpLink: 'article/dataops-observability-help/view-events-and-runs '
        },
        children: [
          {
            path: '',
            pathMatch: 'full',
            redirectTo: 'all',
          },
          {
            path: 'all',
            component: EventListComponent,
          },
          {
            path: 'runs',
            component: BatchRunsComponent,
          },
        ]
      },
      {
        path: 'runs/details',
        loadChildren: () => import('../runs/runs.module').then((m) => m.RunsModule),
      }
    ])
  ],
  exports: [ RouterModule ]
})
export class EventsRoutingModule {}
