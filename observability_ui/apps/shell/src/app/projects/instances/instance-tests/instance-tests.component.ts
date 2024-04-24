import { Component } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { ActivatedRoute } from '@angular/router';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { TestOutcomeItem, TestStatus, TestsSearchFields } from '@observability-ui/core';
import { MetadataViewerComponent, MetadataViewerData, TableChangeEvent } from '@observability-ui/ui';
import { BehaviorSubject, Subject, filter, map } from 'rxjs';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { getCompleteSummary } from '../../task-test-summary/task-test-summary.utils';

@Component({
  selector: 'shell-instance-tests',
  templateUrl: 'instance-tests.component.html',
  styleUrls: [ 'instance-tests.component.scss' ]
})
export class InstanceTestsComponent extends CoreComponent implements HasSearchForm<TestsSearchFields> {
  projectId: string;
  instanceId: string;


  testStatus = TestStatus;
  testStatuses = [ TestStatus.Passed, TestStatus.Warning, TestStatus.Failed ];

  @BindToQueryParams()
  @PersistOnLocalStorage()
  search = new TypedFormGroup<TestsSearchFields>({
    search: new TypedFormControl<string>(),
    component_id: new TypedFormControl<string>(),
    status: new TypedFormControl<string>(`${TestStatus.Warning},${TestStatus.Failed}`),
  });

  search$: BehaviorSubject<TestsSearchFields> = new BehaviorSubject<TestsSearchFields>({
    search: '',
    component_id: '',
    status: ''
  });

  components$ = this.store.components$;

  instance$ = this.store.selected$;

  tests$ = this.store.tests$;
  total$ = this.store.testsTotal$;
  testsSummary$ = this.instance$.pipe(
    map(instance => instance?.tests_summary ?? []),
    map((summaries) => getCompleteSummary(summaries)),
  );
  loading$ = this.store.getLoadingFor('getTestsByPage');

  private tableChanged$ = new Subject<TableChangeEvent<TestsSearchFields>>();

  constructor(
    private route: ActivatedRoute,
    private store: InstancesStore,
    private matDialog: MatDialog,
    protected override paramsService: ParameterService,
    protected override storageService: StorageService,
  ) {
    super(paramsService, storageService);
    this.projectId = this.route.snapshot.parent?.params['projectId'];
    this.instanceId = this.route.snapshot.parent?.params['id'];

    this.tableChanged$.pipe(
      takeUntilDestroyed()
    ).subscribe(({ search, ...pagination }) => {
      this.store.dispatch('getTestsByPage', this.projectId, {
        count: pagination.pageSize,
        page: pagination.pageIndex,
        sort: 'desc',
        sort_by: 'start_time',
        filters: this.remapSearchFields(search) as any,
      });

      this.store.dispatch('getOne', this.instanceId);
    });

    this.instance$.pipe(
      filter((instance) => !!instance),
      takeUntilDestroyed(),
    ).subscribe((instance) => this.store.dispatch('findComponents', instance!.journey.id));
  }

  onTableChange($event: TableChangeEvent) {
    this.tableChanged$.next($event);
  }

  viewMetadata(item: TestOutcomeItem): void {
    this.matDialog.open<MetadataViewerComponent, MetadataViewerData>(MetadataViewerComponent, {
      minWidth: 500,
      maxWidth: 500,
      minHeight: 200,
      data: {
        title: 'Test Outcome Metadata',
        all: item,
        metadata: item.metadata ?? {},
        timestamp: item.start_time as string,
      },
    });
  }

  filterByStatus(status: TestStatus): void {
    this.search.patchValue({ status });
  }

  private remapSearchFields({ search, status, component_id }: TestsSearchFields) {
    return {
      search,
      status: status?.split(',').filter(s => s) ?? [],
      component_id: component_id?.split(',').filter(c => c) ?? [],
      instance_id: this.instanceId,
    };
  }
}
