import { Component, OnInit } from '@angular/core';
import { BehaviorSubject, combineLatest, defer, map, merge, Observable, Subject, switchMap, takeUntil, tap } from 'rxjs';
import { beginningOfDay, endOfDay, Instance, ProjectStore, toTimezoneAwareISOString } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { TableChangeEvent } from '@observability-ui/ui';
import { ActivatedRoute } from '@angular/router';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { JourneysService } from '../../../services/journeys/journeys.service';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { AlertsDialogComponent } from '../alerts-dialog/alerts-dialog.component';
import { toSignal } from '@angular/core/rxjs-interop';

interface SearchFields {
  journey_id: string;
  start_range_begin: string;
  start_range_end: string;
  active: string;
  search: string;
}

@Component({
  selector: 'shell-instances-list',
  templateUrl: './instances-list.component.html',
  styleUrls: [ './instances-list.component.scss' ],
})
export class InstancesListComponent extends CoreComponent implements OnInit, HasSearchForm<SearchFields> {
  allJourneys$ = defer(() => this.currentProject$).pipe(
    switchMap(({ id: parentId }) => {
      return this.journeysService.findAll({ parentId });
    }),
    map(({ entities }) => {
      return entities
        .sort((a, b) => a.name?.localeCompare(b.name));
    })
  );

  private projectId = toSignal(
    this.route.params.pipe(
      map(({ projectId }) => projectId)
    )
  );

  now = new Date().getTime();

  storageKey: string;

  instances$ = this.store.list$.pipe(
    map((instances) => {
      return instances.map((instance) => ({
        ...instance,
        start_time: new Date(instance.start_time),
        end_time: instance.end_time ? new Date(instance.end_time) : instance.end_time,
      }));
    })
  );
  total$: Observable<number> = this.store.total$;
  loading$ = merge(
    this.store.getLoadingFor('getPage'),
    defer(() => this.antiFlickerLoading$.asObservable()),
  );

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<SearchFields>({
    journey_id: new TypedFormControl<string>(),
    start_range_begin: new TypedFormControl<string>(),
    start_range_end: new TypedFormControl<string>(),
    active: new TypedFormControl<string>(),
    search: new TypedFormControl<string>()
  });

  search$ = new BehaviorSubject<SearchFields>({
    journey_id: '',
    start_range_begin: '',
    start_range_end: '',
    active: '',
    search: '',
  });

  filtersApplied$ = this.search$.pipe(
    map(({ journey_id, start_range_begin, start_range_end, active, search }) => !!journey_id || !!start_range_begin || !!start_range_end || !!active || !!search),
  );
  antiFlickerLoading$ = new BehaviorSubject(true);

  private tableChange$ = new Subject<TableChangeEvent<SearchFields>>();
  private currentProject$ = this.projectStore.current$;

  constructor(
    storageService: StorageService,
    paramsService: ParameterService,
    private store: InstancesStore,
    private route: ActivatedRoute,
    private journeysService: JourneysService,
    private projectStore: ProjectStore,
    private matDialog: MatDialog
  ) {
    super(paramsService, storageService);
    this.storageKey = [ this.route.snapshot?.params['projectId'], 'Instances', '' ].join(':');
  }

  override ngOnInit(): void {


    combineLatest([
      this.tableChange$.pipe(
        map(({ search, ...page }) => {
          return {
            ...page,
            search: this.remapSearchFields(search)
          };
        })
      ),
      this.currentProject$,
    ]).pipe(
      takeUntil(this.destroyed$),
    ).subscribe(([ { pageIndex: page, pageSize: count, search: filters }, project ]) => {
      this.store.dispatch('getPage', {
        page,
        count,
        filters,
        sort: 'desc',
        parentId: project.id,
      });
    });

    this.search$.pipe(
      tap(() => this.antiFlickerLoading$.next(true)),
      takeUntil(this.destroyed$),
    ).subscribe();

    super.ngOnInit();
  }

  onTableChange(page: TableChangeEvent<SearchFields>) {
    this.tableChange$.next(page);
  }

  remapSearchFields({ journey_id, start_range_begin, start_range_end, active, search }: SearchFields) {
    const activeValues = active?.split(',');

    const searchModel = {
      journey_id: journey_id?.split(',')?.filter(n => n) || [],
      start_range_begin: '',
      start_range_end: '',
      search,
      active: activeValues?.length == 2 ? '' : active,
    };

    if (start_range_begin) {
      const startDate = beginningOfDay(new Date(start_range_begin));
      searchModel.start_range_begin = toTimezoneAwareISOString(startDate);
    }

    if (start_range_end) {
      const endDate = endOfDay(new Date(start_range_end));
      searchModel.start_range_end = toTimezoneAwareISOString(endDate);
    }

    return searchModel;
  }

  openAlertsDialog(instance: Instance) {
    this.matDialog.open(AlertsDialogComponent, {
      width: '80%',
      data: {
        instanceId: instance.id,
        projectId: this.projectId(),
        journeyId: instance.journey.id,
        instance: instance
      }
    });
  }
}
