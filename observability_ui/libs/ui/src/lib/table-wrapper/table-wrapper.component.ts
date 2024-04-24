import { AfterViewInit, Component, ContentChildren, EventEmitter, Input, OnInit, Output, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { SelectionModel } from '@angular/cdk/collections';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { MatLegacyColumnDef as MatColumnDef } from '@angular/material/legacy-table';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { MatSort } from '@angular/material/sort';
import { map, startWith, takeUntil, tap } from 'rxjs/operators';
import { BehaviorSubject, combineLatest, debounceTime } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { CoreComponent, HasPaginator, HasSearchForm, HasSorting, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { SortDisabledDirective } from './sort-disabled.directive';
import { ToggleDisabledDirective } from './toggle-disabled.directive';
import { DragDisabledDirective } from './drag-disabled.directive';
import { HeaderLabelDirective } from './header-label.directive';
import { TableChangeEvent } from './table-wrapper.model';

interface Column {
  name: string;
  visible: boolean;
}

@Component({
  selector: 'table-wrapper',
  templateUrl: 'table-wrapper.component.html',
  styleUrls: [ 'table-wrapper.component.scss' ],
})
export class TableWrapperComponent extends CoreComponent implements OnInit, AfterViewInit, HasPaginator, HasSorting, HasSearchForm<any> {

  @ViewChildren(MatColumnDef)
  _columns!: QueryList<MatColumnDef>;

  @ViewChild(MatSort) __sortBy!: MatSort;

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  @ContentChildren(MatColumnDef)
  _columnTemplates!: QueryList<MatColumnDef>;

  @ContentChildren(SortDisabledDirective)
  _matSortDisabledColumns!: QueryList<SortDisabledDirective>;

  @ContentChildren(ToggleDisabledDirective)
  _toggleDisabledColumns!: QueryList<ToggleDisabledDirective>;

  @ContentChildren(DragDisabledDirective)
  _dragDisabledDirective!: QueryList<DragDisabledDirective>;

  @ContentChildren(HeaderLabelDirective)
  _headerLabels!: QueryList<HeaderLabelDirective>;

  @Input()
  public items: Array<{ id: number | string; [k: string]: any }> = [];

  @Input()
  public total!: number;

  @Input()
  public columns: (string | Column)[] = [];


  @Input()
  public loading!: boolean;

  @Input()
  public entity!: string;

  @Input()
  public search!: TypedFormGroup<any>;

  @Input()
  public disablePagination: boolean = false;

  @Input()
  public selectable: boolean = true;

  @Input()
  public storageKeyNamespace!: string;

  @Output()
  public reload: EventEmitter<void> = new EventEmitter<void>();

  @Output()
  public tableChange: EventEmitter<TableChangeEvent> = new EventEmitter<TableChangeEvent>();

  public selection: SelectionModel<string> = new SelectionModel<string>(true);

  public pageSize: number = 50;

  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  public tableColumns$ = new BehaviorSubject<{
    name: string;
    visible: boolean;
  }[]>([]);

  public visibleColumns$ = this.tableColumns$.pipe(
    map((columns) => {
      return columns
        .filter(c => c.visible)
        .map((c) => c.name);
    }),
  );

  public storageKey!: string;
  public isOpen!: boolean;

  search$ = new BehaviorSubject('');

  headerLabels!: { [column: string]: HeaderLabelDirective | undefined };

  columnNames!: string[];

  constructor(
    protected parameterService: ParameterService,
    protected override storageService: StorageService,
    private route: ActivatedRoute,
  ) {
    super(parameterService, storageService);
  }

  override ngOnInit(): void {
    // set storage key before super.ngOnInit otherwise `Prop` function would not be able to resolve `storageKey`
    // add an extra `` empty string to force e trailing `:`
    this.storageKey = [ this.route.snapshot.url.toString(), this.entity, this.storageKeyNamespace ?? '' ].join(':');

    super.ngOnInit();

    if (this.selectable) {
      this.columns.unshift('select');
    }

    this.columnNames = this.columns.map((c) => {
      if (typeof c === 'string') {
        return c;
      }
      return c.name;
    });

    const columns = this.columns.map((c) => {
      if (typeof c === 'string') {
        return {
          name: c,
          visible: true,
        };
      }

      return c;
    });

    const storedColumnNames = this.tableColumns$.value.map(c => c.name);
    const shouldReset = !this.columnNames.every(c => storedColumnNames.includes(c)) || !storedColumnNames.every(c => this.columnNames.includes(c));

    if (shouldReset) {
      // do this only if columns are not retrieved from localStorage or if input is changed.
      // I.e.: we don't want input for changes here but after deploy of a new version we may have changed the columns
      // breaking the app here
      this.tableColumns$.next(columns);
    }

    combineLatest([
      this.__pageChange$,
      this.__sortChange$,
      this.search$,
      this.reload.pipe(
        startWith(true),
      ),
    ]).pipe(
      // allow some slack time to wait for all updated to pageChange or sortChanged
      // due to other directives
      // this slack time should be greater than the slack time already allowed in
      // CoreComponent
      debounceTime(this.defaultDebounce + 200, this.scheduler),
      tap(([ page, sort, search ]) => {
        this.tableChange.next({
          ...page,
          sort,
          search,
        });
      }),
      takeUntil(this.destroyed$),
    ).subscribe();

  }

  override ngAfterViewInit() {
    super.ngAfterViewInit();

    this.headerLabels = this.columnNames.reduce<{
      [column: string]: HeaderLabelDirective | undefined
    }>((headers, column) => {
      headers[column] = this.getHeaderLabels(column);

      return headers;
    }, {});
  }

  /** Selects all rows in current page if they are not all selected; otherwise clear selection. */
  masterToggle(): void {
    if (this.isAllSelected()) {
      this.selection.clear();
    } else {
      this.selection.select(...this.items.map(i => i.id as string));
    }
  }

  /** Whether all items in current page are selected */
  isAllSelected(): boolean {
    if (this.disablePagination) {
      return this.selection.selected.length === this.items.length;
    } else {
      const numSelected = this.selection.selected.length;
      const numRows = Math.min(this.paginator.pageSize, this.items.length);
      return numSelected === numRows;
    }
  }

  onReload(): void {
    this.reload.next();
  }

  isDefinedInParent(colName: string): boolean {
    return this._columnTemplates.some((colDef) => colDef.name === colName);
  }

  dropListDropped({
                    previousIndex,
                    currentIndex
                  }: Pick<CdkDragDrop<any, any>, 'previousIndex' | 'currentIndex'>): void {
    const columns = this.tableColumns$.value;


    let undefinedCount = 0;
    const arrayForIndexCorrection = columns.map((c, idx) => {
      if (!c.visible) {
        undefinedCount++;
        return undefined;
      }

      return idx - undefinedCount;
    });


    // +1 to take in account the `select` column
    const realCurrentIndex = arrayForIndexCorrection.indexOf(currentIndex + 1);
    const realPreviousIndex = arrayForIndexCorrection.indexOf(previousIndex + 1);

    // check if target position is a column with dragDisabled
    const targetColumn = columns[realCurrentIndex];
    const hasDragDisabled = this.hasDragDisabled(targetColumn.name);

    if (!hasDragDisabled) {

      moveItemInArray(columns, realPreviousIndex, realCurrentIndex);
      this.tableColumns$.next(columns);

    }
  }

  getColumn(name: string): MatColumnDef | null {
    return this._columnTemplates.find((col) => col.name === name) || null;
  }

  private getHeaderLabels(name: string) {
    return this._headerLabels.find((col) => col.headerLabel === name);
  }

  hasSortDisabled(colName: string): boolean {
    return !!this._matSortDisabledColumns.find((column) => column.columnName === colName)?.disabled;

  }

  hasToggleDisabled(colName: string): boolean {
    return !!this._toggleDisabledColumns.find((c) => c.columnName === colName)?.disabled;
  }

  hasDragDisabled(colName: string): boolean {
    return !!this._dragDisabledDirective.find((c) => c.columnName === colName)?.disabled;
  }

  toggleColumnVisibility(col: { name: string; visible: boolean }): void {
    col.visible = !col.visible;
    this.tableColumns$.next(this.tableColumns$.value);
  }
}
