import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';
import { BreadcrumbComponent } from './breadcrumb.component';


@NgModule({
  imports: [
    CommonModule,
    MatIconModule,
    RouterModule,
  ],
  exports: [ BreadcrumbComponent ],
  declarations: [ BreadcrumbComponent ],
  providers: [],
})
export class BreadcrumbModule {
}
