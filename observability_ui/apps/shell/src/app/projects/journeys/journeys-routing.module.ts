import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { JourneyRelationshipsComponent } from './journey-relationships/journey-relationships.component';
import { JourneysListComponent } from './journeys-list/journeys-list.component';
import { JourneySettingsComponent } from './journey-settings/journey-settings.component';
import { JourneyDetailsComponent } from './journey-details/journey-details.component';
import { JourneyRulesComponent } from './journey-rules/journey-rules.component';

@NgModule({
  imports: [
    RouterModule.forChild([
      {
        path: '',
        component: JourneysListComponent,
        data: {
          helpLink: 'journeys/'
        },
      },
      {
        path: ':id',
        component: JourneyDetailsComponent,
        data: {
          helpLink: 'journeys/journey-details/'
        },
        children: [
          {
            path: '',
            pathMatch: 'full',
            redirectTo: 'relationships',
          },
          {
            path: 'relationships',
            component: JourneyRelationshipsComponent,
          },
          {
            path: 'settings',
            component: JourneySettingsComponent
          },
          {
            path: 'rules',
            component: JourneyRulesComponent,
            data: {
              helpLink: 'rules/'
            },
          },
        ]
      },
    ])
  ],
  exports: [ RouterModule ]
})
export class JourneysRoutingModule {
}
