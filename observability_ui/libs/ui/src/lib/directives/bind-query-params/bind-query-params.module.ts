import { NgModule } from '@angular/core';
import { BindQueryParamsMatTabDirective } from './to-mat-tab/bind-query-params-mat-tab.directive';
import { BindQueryParamsMatSortDirective } from './to-mat-sort/bind-query-params-mat-sort.directive';
import { BindQueryParamsMatPaginatorDirective } from './to-mat-paginator/bind-query-params-mat-paginator.directive';
import { MatSortModule } from '@angular/material/sort';

const exportables = [
  BindQueryParamsMatTabDirective,
  BindQueryParamsMatSortDirective,
  BindQueryParamsMatPaginatorDirective,
];

@NgModule({
  imports: [
    MatSortModule,
  ],
  exports: [
    exportables
  ],
  declarations: [
    exportables
  ],
  providers: [],
})
export class  BindQueryParamsModule {
}
