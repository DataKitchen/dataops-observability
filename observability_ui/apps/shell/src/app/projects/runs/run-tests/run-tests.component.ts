import { Component, OnInit } from '@angular/core';
import { TestOutcomeItem, TestStatus, TestsSearchFields } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasSearchForm, ParameterService, PersistOnLocalStorage, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { BehaviorSubject, map, Subject, takeUntil } from 'rxjs';
import { MetadataViewerComponent, MetadataViewerData, TableChangeEvent } from '@observability-ui/ui';
import { ActivatedRoute } from '@angular/router';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { RunsStore } from '../../../stores/runs/runs.store';
import { getCompleteSummary } from '../../task-test-summary/task-test-summary.utils';

@Component({
  selector: 'shell-run-tests',
  templateUrl: 'run-tests.component.html',
  styleUrls: [ 'run-tests.component.scss' ],
})
export class RunTestsComponent extends CoreComponent implements OnInit, HasSearchForm<TestsSearchFields> {
  projectId: string;
  runId: string;


  testStatus = TestStatus;
  testStatuses = [ TestStatus.Passed, TestStatus.Warning, TestStatus.Failed ];

  @BindToQueryParams()
  @PersistOnLocalStorage()
  search = new TypedFormGroup<TestsSearchFields>({
    search: new TypedFormControl<string>(),
    component_id: new TypedFormControl<string>(),
    status: new TypedFormControl<string>(),
  });

  search$: BehaviorSubject<TestsSearchFields> = new BehaviorSubject<TestsSearchFields>({
    search: '',
    component_id: '',
    status: ''
  });

  tests$ = this.store.tests$;
  total$ = this.store.testsTotal$;

  run$ = this.store.selected$;

  testsSummary$ = this.run$.pipe(
    map(instance => instance?.tests_summary ?? []),
    map((summaries) => getCompleteSummary(summaries)),
  );

  loading$ = this.store.getLoadingFor('getTestsByPage');

  private tableChanged$ = new Subject<TableChangeEvent<TestsSearchFields>>();

  constructor(
    private route: ActivatedRoute,
    public store: RunsStore,
    private matDialog: MatDialog,
    protected override paramsService: ParameterService,
    protected override storageService: StorageService,
  ) {
    super(paramsService, storageService);
    this.projectId = this.route.snapshot.parent?.params['projectId'];
    this.runId = this.route.snapshot.parent?.params['runId'];
  }

  override ngOnInit() {
    this.tableChanged$.pipe(
      takeUntil(this.destroyed$)
    ).subscribe(({ search, ...pagination }) => {
      this.store.dispatch('getTestsByPage', this.projectId, {
        count: pagination.pageSize,
        page: pagination.pageIndex,
        sort: 'desc',
        sort_by: 'start_time',
        filters: this.remapSearchFields(search) as any,
      });

      this.store.dispatch('getOne', this.runId);
    });

    super.ngOnInit();
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
      run_id: this.runId,
    };
  }
}
