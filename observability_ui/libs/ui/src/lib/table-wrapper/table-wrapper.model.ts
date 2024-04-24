import { Sort } from '@angular/material/sort';

export interface TableChangeEvent<TSearch = any> {
  pageIndex: number;
  pageSize: number;
  sort?: Sort;
  search: TSearch;
}
