import { Component, OnInit } from '@angular/core';
import { EventSearchFields, EventType, EventTypes, ProjectStore } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { ComponentStore } from '../../components/components.store';
import { BehaviorSubject, combineLatest, defer, map, merge, Observable, Subject, takeUntil, tap } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { TableChangeEvent } from '@observability-ui/ui';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'shell-event-list',
  templateUrl: 'event-list.component.html',
  styleUrls: [ 'event-list.component.scss' ]
})
export class EventListComponent extends CoreComponent implements OnInit, HasSearchForm<EventSearchFields> {
  storageKey!: string;

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<EventSearchFields>({
    component_id: new TypedFormControl<string>(),
    event_type: new TypedFormControl<string>(),
  });

  search$: BehaviorSubject<EventSearchFields> = new BehaviorSubject<EventSearchFields>({
    component_id: '',
    event_type: ''
  });

  readonly events = EventTypes;

  parentId: string;
  components$ = this.componentStore.select(({ all }) => all);
  events$: Observable<EventType[]> = this.projectStore.events$;
  total$ = this.projectStore.totalEvents$;
  loading$ = merge(
    this.projectStore.getLoadingFor('getEventsByPage'),
    defer(() => this.antiFlickerLoading$.asObservable()),
  );
  componentsLoading = toSignal(this.componentStore.getLoadingFor('searchPage'));

  filtersApplied$ = this.search$.pipe(
    map(({ component_id, event_type }) => !!component_id || !!event_type),
  );
  antiFlickerLoading$ = new BehaviorSubject(true);

  private tableChanged$ = new Subject<TableChangeEvent<EventSearchFields>>();

  constructor(
    private componentStore: ComponentStore,
    private route: ActivatedRoute,
    private projectStore: ProjectStore,
    protected override paramsService: ParameterService,
    protected override storageService: StorageService,
  ) {
    super(paramsService, storageService);

    this.storageKey = [ this.route.parent?.snapshot.params['projectId'], 'events', '' ].join(':');
  }

  override ngOnInit() {
    this.projectStore.current$.pipe(
      takeUntil(this.destroyed$)
    ).subscribe(({ id }) => {

      this.parentId = id;

      const ids = this.search.value.component_id?.split(',') || [];
      this.componentStore.dispatch('searchPage', { parentId: id, count: 20, page: 0 }, ids);
    });

    combineLatest([
      this.projectStore.current$,
      this.tableChanged$,
    ]).pipe(
      takeUntil(this.destroyed$)
    ).subscribe(([ { id }, { search: { event_type, component_id }, ...pagination } ]) => {

      const eventTypes = event_type?.split(',').filter(e => e) ?? [];
      const components = component_id?.split(',').filter(e => e) ?? [];

      this.projectStore.dispatch('getEventsByPage', {
        parentId: id,
        count: pagination.pageSize,
        page: pagination.pageIndex,
        sort: 'desc',
        filters: {
          event_type: eventTypes as any,
          component_id: components as any,
        },
      });

      this.search$.pipe(
        tap(() => this.antiFlickerLoading$.next(true)),
        takeUntil(this.destroyed$),
      ).subscribe();
    });

    super.ngOnInit();
  }

  onTableChange($event: TableChangeEvent<EventSearchFields>) {
    this.tableChanged$.next($event);
  }

  onComponentSearch(value: string) {
    const ids = this.search.value.component_id?.split(',') || [];

    this.componentStore.dispatch('searchPage', {
      parentId: this.parentId,
      count: 20,
      page: 0,
      filters: { search: value !== '' ? value : null }
    }, ids);
  }
}
