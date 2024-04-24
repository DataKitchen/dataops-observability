import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ComponentsListComponent } from './components-list/components-list.component';

@NgModule({
  imports: [
    RouterModule.forChild([
      {
        path: '',
        component: ComponentsListComponent,
        data: {
          helpLink: 'article/dataops-observability-help/components'
        },
      },
    ]),

  ],
  exports: [ RouterModule ],
})
export class ComponentsRoutingModule {
}
