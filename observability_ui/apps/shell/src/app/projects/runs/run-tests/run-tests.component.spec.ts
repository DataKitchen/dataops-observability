import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RunTestsComponent } from './run-tests.component';
import { MockComponent, MockModule, MockProvider } from 'ng-mocks';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { RunsStore } from '../../../stores/runs/runs.store';
import { ComponentType, TestOutcomeItem, TestStatus } from '@observability-ui/core';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { DkTooltipModule, FilterFieldComponent, FilterFieldOptionComponent, MetadataViewerComponent, TableWrapperComponent, TextFieldModule } from '@observability-ui/ui';
import { Mocked } from '@datakitchen/ngx-toolkit';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MatDialogModule } from '@angular/material/dialog';
import { SummaryComponent } from '../../../components/summary/summary.component';
import { SummaryItemComponent } from '../../../components/summary-item/summary-item.component';
import { ReactiveFormsModule } from '@angular/forms';

describe('Run Tests', () => {
  const id = '123';
  const testOutcome: TestOutcomeItem = {
    name: 'Address column is correctly formatted',
    status: TestStatus.Warning,
    description: 'row_count',
    min_threshold: 5,
    max_threshold: 10,
    metric_value: 500,
    start_time: '2023-01-01T17:08:02',
    end_time: '2023-01-01T20:08:02',
    component: { id: '1', display_name: 'Python Create Star Schema', type: ComponentType.BatchPipeline },
    metadata: { key: 'value' },
  } as TestOutcomeItem;

  let fixture: ComponentFixture<RunTestsComponent>;
  let component: RunTestsComponent;

  let matDialog: Mocked<MatDialog>;
  let store: Mocked<RunsStore>;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      declarations: [
        RunTestsComponent,
        TranslatePipeMock,
        MockComponent(FilterFieldComponent),
        MockComponent(FilterFieldOptionComponent),
        MockComponent(TableWrapperComponent),
      ],
      imports: [
        MockModule(MatDialogModule),
        DkTooltipModule,
        TextFieldModule,
        ReactiveFormsModule,
        BrowserAnimationsModule,
        SummaryComponent,
        SummaryItemComponent
      ],
      providers: [
        MockProvider(RunsStore, {
          selected$: of({ journey: { id: '12' }, tests_summary: [ { status: TestStatus.Warning, count: 1 } ] }),
          tests$: of([]),
          testsTotal$: of(0),
          components$: of([]),
          dispatch: jest.fn(),
          getLoadingFor: jest.fn().mockReturnValue(of(false)),
        } as any),
        MockProvider(ActivatedRoute, {
          queryParams: of({}),
          snapshot: {
            params: { projectId: '123' },
            parent: { params: { runId: id } },
            url: 'test'
          },
          parent: {
            params: of({ id })
          },
        } as any),
        MockProvider(MatDialog),
      ]
    });

    matDialog = TestBed.inject(MatDialog) as Mocked<MatDialog>;
    matDialog.open = jest.fn();

    store = TestBed.inject(RunsStore) as Mocked<RunsStore>;

    fixture = TestBed.createComponent(RunTestsComponent);
    component = fixture.componentInstance;

    component.search.patchValue = jest.fn();

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get the list of tests sorted by start time', () => {
    component['tableChanged$'].next({pageIndex: 0, pageSize: 50, search: {} as any });
    expect(store.dispatch).toBeCalledWith('getTestsByPage', undefined, expect.objectContaining({sort: 'desc', sort_by: 'start_time'}));
  });

  it('should refresh header details', () => {
    component['tableChanged$'].next({pageIndex: 0, pageSize: 50, search: {} as any });
    expect(store.dispatch).toBeCalledWith('getOne', id);
  });

  describe('viewMetadata()', () => {
    it('should open the metadata dialog', () => {
      component.viewMetadata(testOutcome);
      expect(matDialog.open).toBeCalledWith(MetadataViewerComponent, {
        minWidth: 500,
        maxWidth: 500,
        minHeight: 200,
        data: {
          title: 'Test Outcome Metadata',
          all: testOutcome,
          metadata: testOutcome.metadata,
          timestamp: testOutcome.start_time,
        },
      });
    });
  });

  describe('filterByStatus', () => {
    it('should patch the status value to the search', () => {
      component.filterByStatus(TestStatus.Passed);
      expect(component.search.patchValue).toHaveBeenCalledWith({ status: TestStatus.Passed });
    });
  });
});
