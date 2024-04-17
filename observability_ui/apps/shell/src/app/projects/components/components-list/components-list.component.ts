import { Component, OnInit, QueryList, ViewChild, ViewChildren, ViewContainerRef } from '@angular/core';
import { ComponentType, ProjectStore, } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasPaginator, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { BehaviorSubject, combineLatest, debounceTime, defer, filter, map, merge, takeUntil, tap } from 'rxjs';
import { AddComponentDialogComponent } from '../add-component-dialog/add-component-dialog.component';
import { ComponentStore } from '../components.store';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { ActivatedRoute } from '@angular/router';
import { MatLegacyCheckbox } from '@angular/material/legacy-checkbox';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { MultipleDeleteDialogComponent } from '../multiple-delete-dialog/multiple-delete-dialog.component';
import { MultipleJourneyDialogComponent } from '../multiple-journey-dialog.component.ts/multiple-journey-dialog.component';
import { MatLegacyDialog } from '@angular/material/legacy-dialog';
import { BreakpointObserver } from '@angular/cdk/layout';

interface SearchFields {
  search: string;
  component_type: string;
  tool: string;
}

@Component({
  selector: 'shell-components-list',
  templateUrl: './components-list.component.html',
  styleUrls: [ './components-list.component.scss' ]
})
export class ComponentsListComponent extends CoreComponent implements OnInit, HasPaginator, HasSearchForm<SearchFields> {
  @ViewChildren('componentCheckbox') checkboxes: QueryList<MatLegacyCheckbox>;

  loading$ = merge(
    this.store.getLoadingFor('getPage'),
    defer(() => this.antiFlickerLoading$.asObservable()),
  );
  total$ = this.store.total$;
  selectedComponents: string[] = [];

  allComponents = toSignal(this.store.allComponents$);

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<SearchFields>({
    search: new TypedFormControl(''),
    component_type: new TypedFormControl(''),
    tool: new TypedFormControl(''),
  });

  search$ = new BehaviorSubject<SearchFields>({
    search: '',
    component_type: '',
    tool: '',
  });

  storageKey!: string;
  parentId: string;
  pageSize: number = 10;
  componentTypes = Object.values(ComponentType).sort((a, b) => a > b ? 1 : a < b ? -1 : 0);

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  components$ = this.store.list$;
  filtersApplied$ = this.search$.pipe(
    map(({ search, component_type, tool }) => !!search || !!component_type || !!tool),
  );
  antiFlickerLoading$ = new BehaviorSubject(true);

  isSmallScreen$ = this.breakpointObserver.observe([ '(max-width: 1199px)' ]).pipe(
    map(state => state.matches),
  );

  constructor(
    private matDialog: MatLegacyDialog,
    private viewContainerRef: ViewContainerRef,
    private store: ComponentStore,
    protected paramService: ParameterService,
    protected override storageService: StorageService,
    private route: ActivatedRoute,
    private projectStore: ProjectStore,
    private breakpointObserver: BreakpointObserver,
  ) {
    super(paramService, storageService);

    this.store.loading$.pipe(
      filter(({ code }) => code === 'updateOne'),
      filter(({ status }) => status === false),
      tap(() => this.selectedComponents = []),
      takeUntilDestroyed(),
    ).subscribe();
  }

  override ngOnInit() {
    this.storageKey = [ this.route.snapshot.params['projectId'], 'ComponentsList', '' ].join(':');

    super.ngOnInit();

    combineLatest([
      this.projectStore.current$,
      this.__pageChange$,
      this.search$.pipe(
        tap(() => this.antiFlickerLoading$.next(true)),
      ),
    ]).pipe(
      debounceTime(this.defaultDebounce + 20, this.scheduler),
      takeUntil(this.destroyed$),
    ).subscribe(([ project, { pageIndex, pageSize }, { search, component_type, tool } ]) => {
      const componentTypes = component_type?.split(',').filter(e => e) ?? [];

      this.parentId = project.id;
      this.pageSize = pageSize;

      this.store.dispatch('getPage', {
        page: pageIndex,
        count: pageSize,
        parentId: project.id,
        filters: {
          component_type: componentTypes as any,
          search: search as any,
          tool: tool?.split(',').filter(e => e) ?? [],
        }
      });
    });
  }

  openAddComponentDialog(): void {
    this.matDialog.open(AddComponentDialogComponent, {
      width: '500px',
      autoFocus: false,
      viewContainerRef: this.viewContainerRef
    });
  }

  onCheckboxToggle(id: string, checkbox: MatLegacyCheckbox) {
    checkbox.checked = !checkbox.checked;

    if (this.selectedComponents.includes(id)) {
      const index = this.selectedComponents.indexOf(id);
      this.selectedComponents.splice(index, 1);
    } else {
      this.selectedComponents.push(id);
    }
  }

  onClearSelection() {
    this.checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });

    this.selectedComponents = [];
  }


  onSelectAll() {
    this.checkboxes.forEach((checkbox) => {
      checkbox.checked = true;

      if (!this.selectedComponents.includes(checkbox.value)) {
        this.selectedComponents.push(checkbox.value);
      }
    });
  }

  showMultipleDeleteDialog() {
    const dialogRef = this.matDialog.open(MultipleDeleteDialogComponent, {
      width: '600px',
      data: {
        ids: this.selectedComponents,
        components: this.allComponents().filter((comp) => this.selectedComponents.includes(comp.id)),
        projectId: this.parentId
      }
    });

    dialogRef.afterClosed().subscribe((data: { ids: string[] }) => {
      if (data) {
        data.ids.forEach((id) => {
          this.store.dispatch('deleteComponent', id);
        });

        this.selectedComponents = [];
      }
    });
  }

  showCreateJourneyDialog() {
    this.matDialog.open(MultipleJourneyDialogComponent, {
      width: '600px',
      data: {
        ids: this.selectedComponents,
        components: this.allComponents().filter((comp) => this.selectedComponents.includes(comp.id)),
        projectId: this.parentId
      }
    });
  }
}
