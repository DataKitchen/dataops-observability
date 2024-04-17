import { Directive, Input, OnChanges, Optional, SimpleChanges } from '@angular/core';
import { MatLegacyPaginator as MatPaginator, LegacyPageEvent as PageEvent } from '@angular/material/legacy-paginator';
import { Params } from '@angular/router';
import { BindQueryParamsAbstract } from '../bind-query-params.abstract';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';

@Directive({selector: '[bindQueryParamsMatPaginator]'})
export class BindQueryParamsMatPaginatorDirective extends BindQueryParamsAbstract implements OnChanges {

  private separator = '_';

  @Input() pageIndex!: number;
  @Input() pageSize!: number;
  @Input() queryParamsNamespace!: string;

  // eslint-disable-next-line @angular-eslint/no-input-rename
  @Input('sizeStorageKey') storageKey!: string;

  constructor(
    protected override parameterService: ParameterService,
    protected paginator: MatPaginator,
    @Optional() protected storage: StorageService,
  ) {
    super(parameterService, paginator.page);
  }

  ngOnChanges({pageIndex, pageSize, }: SimpleChanges): void {
    if (!(pageIndex?.firstChange || pageSize.firstChange)) {

      if (pageIndex.currentValue || pageSize.currentValue) {
        this.paginator.page.next({pageIndex: this.pageIndex, pageSize: this.pageSize} as PageEvent);
      }

    }

  }

  protected override parseInitialValue(params: Params): { pageSize: number; pageIndex: number|undefined } {
    const pageSizeKey = [ this.queryParamsNamespace, 'pageSize' ].join(this.separator);
    const pageIndexKey = [ this.queryParamsNamespace, 'pageIndex' ].join(this.separator);
    const pageSize = (params[pageSizeKey] ? Number(params[pageSizeKey]) : (this.storageKey ? this.storage.getStorage(this.storageKey) : undefined)) as number;
    const pageIndex = params[pageIndexKey] ? Number(params[pageIndexKey]) : undefined;
    return {pageSize, pageIndex};
  }

  protected setInitialValue({pageIndex = this.pageIndex, pageSize = this.pageSize}: PageEvent): void {
    void Promise.resolve().then(() => {

      this.pageIndex = pageIndex;
      this.pageSize = pageSize;
      this.paginator.pageIndex = pageIndex;
      this.paginator.pageSize = pageSize;
      this.paginator.page.next({pageIndex, pageSize} as PageEvent);
    });
  }

  override parseValuesToParams({pageIndex, pageSize}: PageEvent): Pick<PageEvent, 'pageIndex' & 'pageSize'> {
    if (this.storageKey) {
      this.storage.setStorage(this.storageKey, pageSize);
    }

    return {
      [[ this.queryParamsNamespace, 'pageIndex' ].join(this.separator)]: pageIndex || null, // Remove if 0
      [[ this.queryParamsNamespace, 'pageSize' ].join(this.separator)]: pageSize,
    };
  }
}
