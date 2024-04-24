import { Directive, Self } from '@angular/core';
import { MatSort, Sort, SortDirection } from '@angular/material/sort';
import { BindQueryParamsAbstract } from '../bind-query-params.abstract';
import { ParameterService } from '@datakitchen/ngx-toolkit';

@Directive({selector: '[bindQueryParamsMatSort]'})
export class BindQueryParamsMatSortDirective extends BindQueryParamsAbstract {

  constructor(
    protected override parameterService: ParameterService,
    @Self() protected sort: MatSort,
  ) {
    super(parameterService, sort.sortChange);
  }

  protected setInitialValue({sortBy, sortOrder}: { sortBy: string; sortOrder: SortDirection }): void {
    void Promise.resolve().then(() => {
      if (sortBy || sortOrder) {
        this.sort.sort({id: sortBy, start: sortOrder as 'asc' | 'desc', disableClear: true});
      }
    });
  }

  override parseValuesToParams({active, direction}: Sort): { sortBy: string|null; sortOrder: SortDirection|null } {
    // Ony write params with both values present
    return {
      sortBy: (direction && active) ? active  : null,
      sortOrder: (active && direction) ? direction : null,
    };
  }
}
