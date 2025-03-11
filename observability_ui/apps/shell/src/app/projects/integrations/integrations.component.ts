import { Component, OnInit, ViewChild } from '@angular/core';
import { BehaviorSubject, combineLatest, debounceTime, defer, filter, map, merge, takeUntil, tap, timer } from 'rxjs';
import { AgentStatus, AgentStore, ProjectStore } from '@observability-ui/core';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { ActivatedRoute } from '@angular/router';
import { CoreComponent, HasPaginator, HasSearchForm, BindToQueryParams, PersistOnLocalStorage, Prop, TypedFormGroup, TypedFormControl, StorageService, ParameterService } from '@datakitchen/ngx-toolkit';

type SearchFields = { search: string; };

@Component({
  selector: 'shell-integrations',
  templateUrl: 'integrations.component.html',
  styleUrls: [ 'integrations.component.scss' ]
})
export class IntegrationsComponent extends CoreComponent implements OnInit, HasPaginator, HasSearchForm<SearchFields> {
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  readonly AgentStatus = AgentStatus;

  loading$ = merge(
    this.agentStore.getLoadingFor('getPage'),
    defer(() => this.antiFlickerLoading$.asObservable()),
  ).pipe(
    filter(loading => !loading || !this.silentLoading),
  );

  agents$ = this.agentStore.list$;
  total$ = this.agentStore.total$;
  pageSize = 25;

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<SearchFields>({
    search: new TypedFormControl<SearchFields['search']>(),
  });

  search$ = new BehaviorSubject<SearchFields>({
    search: '',
  });

  filtersApplied$ = this.search$.pipe(
    map(({ search }) => !!search),
  );
  antiFlickerLoading$ = new BehaviorSubject(true);
  silentLoading = false;

  storageKey!: string;

  constructor(
    private projectStore: ProjectStore,
    private agentStore: AgentStore,
    protected paramService: ParameterService,
    protected override storageService: StorageService,
    private route: ActivatedRoute,
  ) {

    super(paramService, storageService);

    this.storageKey = [ this.route.snapshot.params['projectId'], 'Integrations', '' ].join(':');
  }

  override ngOnInit() {
    super.ngOnInit();

    combineLatest([
      this.projectStore.selected$,
      this.__pageChange$,
      this.search$.pipe(
        tap(() => {
          this.silentLoading = false;
          this.antiFlickerLoading$.next(true);
        }),
      ),
      timer(0, 30_000, this.scheduler).pipe(
        tap(() => this.silentLoading = true),
      ),
    ]).pipe(
      debounceTime(this.defaultDebounce + 20, this.scheduler),
      takeUntil(this.destroyed$),
    ).subscribe(([ { id: parentId}, { pageIndex: page, pageSize: count }, filters]) => {
      this.agentStore.dispatch('getPage', {
        parentId,
        page,
        count,
        filters,
      });
    });
  }
}
