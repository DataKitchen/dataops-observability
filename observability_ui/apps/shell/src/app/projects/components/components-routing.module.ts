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
          helpLink: 'components/'
        },
      },
    ]),

  ],
  exports: [ RouterModule ],
})
export class ComponentsRoutingModule {
}
