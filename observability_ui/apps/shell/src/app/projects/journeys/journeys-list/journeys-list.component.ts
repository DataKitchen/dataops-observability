import { Component, OnInit, ViewChild, ViewContainerRef } from '@angular/core';
import { CoreComponent, HasPaginator, HasSearchForm, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { JourneysStore } from '../journeys.store';
import { BehaviorSubject, combineLatest, debounceTime, defer, map, merge, takeUntil, tap } from 'rxjs';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { AddJourneyDialogComponent } from '../add-journey-dialog/add-journey-dialog.component';
import { ActivatedRoute } from '@angular/router';
import { ComponentStore } from '../../components/components.store';
import { NoComponentsDialogComponent } from '../no-components-dialog/no-components-dialog.component';
import { toSignal } from '@angular/core/rxjs-interop';
import { ProjectStore } from '@observability-ui/core';

interface SearchFields {
  search: string;
  labels: string;
}

@Component({
  selector: 'shell-journeys-list',
  templateUrl: './journeys-list.component.html',
  styleUrls: [ './journeys-list.component.scss' ]
})
export class JourneysListComponent extends CoreComponent implements OnInit, HasPaginator, HasSearchForm<SearchFields> {
  loading$ = merge(
    this.store.getLoadingFor('getPage'),
    defer(() => this.antiFlickerLoading$.asObservable()),
  );
  total$ = this.store.total$;

  search = new TypedFormGroup<SearchFields>({
    search: new TypedFormControl<string>(),
    labels: new TypedFormControl<string>(),
  });

  search$: BehaviorSubject<SearchFields> = new BehaviorSubject<SearchFields>({ search: '', labels: '' });

  parentId: string;
  pageSize: number = 10;

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  journeys$ = this.store.list$;

  projectHasComponents = toSignal(this.componentsStore.list$.pipe(
    map(list => list.length > 0)
  ));
  components$ = this.componentsStore.list$;

  filtersApplied$ = this.search$.pipe(
    map(({ search, labels }) => !!search || !!labels),
  );
  antiFlickerLoading$ = new BehaviorSubject(true);

  constructor(
    private store: JourneysStore,
    private viewContainerRef: ViewContainerRef,
    private matDialog: MatDialog,
    private route: ActivatedRoute,
    private projectStore: ProjectStore,
    private componentsStore: ComponentStore
  ) {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();

    if (this.route.snapshot.queryParams['openAdd'])
      this.openAddJourneyDialog();

    combineLatest([
      this.projectStore.current$,
      this.__pageChange$,
      this.search$.pipe(
        tap(() => this.antiFlickerLoading$.next(true)),
      ),
    ]).pipe(
      debounceTime(this.defaultDebounce + 20, this.scheduler),
      takeUntil(this.destroyed$)
    ).subscribe(([ project, { pageIndex, pageSize }, { search, labels } ]) => {
      this.parentId = project.id;

      this.componentsStore.dispatch('findAll', { parentId: project.id });

      this.store.dispatch('getPage', {
        page: pageIndex,
        count: pageSize,
        parentId: project.id,
        filters: {
          search,
          labels,
        },
      });
    });
  }

  openAddJourneyDialog(hasComponents: boolean = true): void {
    this.matDialog.open(hasComponents ? AddJourneyDialogComponent : NoComponentsDialogComponent, {
      width: '600px',
      autoFocus: false,
      viewContainerRef: this.viewContainerRef
    });
  }
}
