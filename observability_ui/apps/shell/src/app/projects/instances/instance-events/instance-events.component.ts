import { Component, OnInit } from '@angular/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { EventSearchFields, EventTypes, ProjectStore } from '@observability-ui/core';
import { BehaviorSubject, distinctUntilChanged, filter, map, startWith, Subject, switchMap, takeUntil, tap, withLatestFrom } from 'rxjs';
import { TableChangeEvent } from '@observability-ui/ui';
import { ActivatedRoute } from '@angular/router';
import { InstancesStore } from '../../../stores/instances/instances.store';


@Component({
  selector: 'shell-instance-events',
  templateUrl: './instance-events.component.html',
  styleUrls: [ './instance-events.component.scss' ]
})
export class InstanceEventsComponent extends CoreComponent implements OnInit, HasSearchForm<EventSearchFields> {
  events$ = this.projectStore.events$;
  total$ = this.projectStore.totalEvents$;
  loading$ = this.projectStore.getLoadingFor('getEventsByPage').pipe(
    startWith(true)
  );

  allComponents$ = this.instanceStore.components$.pipe(
    map(components => components.sort((a, b) => a.display_name.localeCompare(b.display_name))),
  );

  storageKey!: string;

  readonly events = EventTypes;

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

  private tableChange$ = new Subject<TableChangeEvent<EventSearchFields>>();

  constructor(
    paramService: ParameterService,
    storageService: StorageService,
    private route: ActivatedRoute,
    private projectStore: ProjectStore,
    private instanceStore: InstancesStore,
  ) {
    super(paramService, storageService);
  }

  override ngOnInit(): void {
    const projectId$ = this.projectStore.current$.pipe(
      map(({ id }) => id),
    );
    const instanceId$ = this.route.parent!.params.pipe(
      map(({ id }) => id),
      tap((instanceId) => this.storageKey = [ instanceId, 'InstanceEvents', '' ].join(':')),
    );

    instanceId$.pipe(
      tap((instanceId) => this.instanceStore.dispatch('getOne', instanceId)),
      switchMap((instanceId) => this.instanceStore.getEntity(instanceId)),
      filter((instance) => !!instance),
      distinctUntilChanged((prev, curr) => prev?.id === curr?.id),
      takeUntil(this.destroyed$),
    ).subscribe((instance) => {
      this.instanceStore.dispatch('findComponents', instance!.journey.id);
    });

    this.tableChange$.pipe(
      withLatestFrom(projectId$, instanceId$, this.allComponents$),
      takeUntil(this.destroyed$),
    ).pipe(
      takeUntil(this.destroyed$),
    ).subscribe(([ {
      search: { event_type, component_id },
      pageIndex,
      pageSize
    }, projectId, instanceId, componentOptions ]) => {
      const components = component_id?.split(',').filter((t: string) => t) || [];
      const eventTypes = event_type?.split(',').filter((e: string) => e) || [];

      this.projectStore.dispatch('getEventsByPage', {
        parentId: projectId,
        sort: 'desc',
        page: pageIndex,
        count: pageSize,
        filters: {
          component_id: components.length === componentOptions.length ? [] : components as any,
          event_type: eventTypes as any,
          instance_id: instanceId,
        },
      });

      this.instanceStore.dispatch('getOne', instanceId);
    });

    super.ngOnInit();
  }

  onTableChange(page: TableChangeEvent<EventSearchFields>) {
    this.tableChange$.next(page);
  }
}
