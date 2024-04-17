import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockComponent, MockComponents, MockDirective, MockModule } from 'ng-mocks';
import { of } from 'rxjs';
import { Project, ProjectService, ProjectStore, Run, RunProcessedStatus } from '@observability-ui/core';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { ActivatedRoute } from '@angular/router';
import { MatSpinner } from '@angular/material/progress-spinner';
import { ProjectRunsService } from '../../../services/project-runs/project-runs.service';
import { MatPaginator } from '@angular/material/paginator';
import { EntityListPlaceholderComponent, FilterFieldModule, TableWrapperComponent, TextFieldModule } from '@observability-ui/ui';
import { MatHeaderRow, MatHeaderRowDef, MatRow, MatRowDef, MatTable } from '@angular/material/table';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ComponentsService } from '../../../services/components/components.service';
import { BatchRunsComponent } from './batch-runs.component';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { RunsModule } from '../../runs/runs.module';
import { ReactiveFormsModule } from '@angular/forms';
import { TranslationModule } from '@observability-ui/translate';
import { ToolSelectorComponent } from '../../integrations/tool-selector/tool-selector.component';
import { RunsStore } from '../../../stores/runs/runs.store';
import { TestScheduler } from '@datakitchen/rxjs-marbles';

describe('batch-runs.component', () => {
  let component: BatchRunsComponent;
  let fixture: ComponentFixture<BatchRunsComponent>;
  let service: ProjectRunsService;

  const testRuns: Run[] = [
    {
      name: 'test-1-run'
    } as Run
  ];
  const mockProject = { id: '342', name: 'My Project' } as Project;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MockModule(MatFormFieldModule),
        MockModule(FilterFieldModule),
        MockModule(RunsModule),
        MockModule(MatDatepickerModule),
        ReactiveFormsModule,
        MockModule(TranslationModule),
        MockModule(TextFieldModule),
      ],
      declarations: [
        BatchRunsComponent,
        MockComponents(MatSpinner),
        MockComponent(EntityListPlaceholderComponent),
        MockComponent(MatTable),
        MockComponent(MatPaginator),
        MockComponent(EntityListPlaceholderComponent),
        MockComponent(MatHeaderRow),
        MockDirective(MatHeaderRowDef),
        MockComponent(MatRow),
        MockDirective(MatRowDef),
        MockComponent(TableWrapperComponent),
        MockComponent(ToolSelectorComponent),
      ],
      providers: [
        MockProvider(ProjectRunsService),
        MockProvider(ProjectService),
        MockProvider(StorageService),
        MockProvider(ParameterService),
        MockProvider(ComponentsService, class {
          findAll = () => of({
            entities: [
              { key: 'cage', display_name: 'cage' },
              { key: 'zero', display_name: 'zero' },
              { key: 'beauty', display_name: 'beauty' },
            ],
          });
        }),
        MockProvider(ActivatedRoute, class {
          snapshot: {
            params: {
              projectId: 1
            }
          };
        }),
        MockProvider(ProjectStore, class {
          current$ = of(mockProject);
        }),
        MockProvider(RunsStore, class {
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        })
      ],
    }).compileComponents();

    service = TestBed.inject(ProjectRunsService);
    service.getPage = jest.fn().mockReturnValue(of(testRuns));

    fixture = TestBed.createComponent(BatchRunsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should provide pipeline names sorted', () => {
    TestScheduler.expect$(component.allPipelines$).toContain([
      expect.objectContaining({ display_name: 'beauty' }),
      expect.objectContaining({ display_name: 'cage' }),
      expect.objectContaining({ display_name: 'zero' }),
    ]);
  });

  describe('#remapSearchFields', () => {

    it('should be defensive', () => {
      expect(component.remapSearchFields({

        pipeline_key: undefined,
        start_range_begin: undefined,
        start_range_end: undefined,
        status: '',
        tool: '',
        search: '',
      })).toEqual({
        pipeline_key: [],
        start_range_begin: '',
        start_range_end: '',
        status: [],
        tool: [],
        search: '',
      });
    });

    it('should remove empty names', () => {
      expect(component.remapSearchFields({
        pipeline_key: 'hello,,mr,me',
        start_range_begin: undefined,
        start_range_end: undefined,
        status: '',
        tool: '',
        search: '',
      })).toEqual({
        pipeline_key: [ 'hello', 'mr', 'me' ],
        start_range_begin: '',
        start_range_end: '',
        status: [],
        tool: [],
        search: '',
      });
    });

    it('should split statuses', () => {
      expect(component.remapSearchFields({
        pipeline_key: '',
        start_range_begin: undefined,
        start_range_end: undefined,
        status: `${RunProcessedStatus.Running},${RunProcessedStatus.Failed}`,
        tool: '',
        search: '',
      })).toEqual({
        pipeline_key: [],
        start_range_begin: '',
        start_range_end: '',
        status: [ RunProcessedStatus.Running, RunProcessedStatus.Failed ],
        tool: [],
        search: '',
      });
    });

    it('should split the tools', () => {
      expect(component.remapSearchFields({
        pipeline_key: '',
        start_range_begin: undefined,
        start_range_end: undefined,
        status: '',
        tool: 'airflow,sqs',
        search: '',
      })).toEqual({
        pipeline_key: [],
        start_range_begin: '',
        start_range_end: '',
        status: [],
        tool: [ 'airflow', 'sqs' ],
        search: '',
      });
    });

    it('should parse start date', () => {
      expect(component.remapSearchFields({
        pipeline_key: undefined,
        start_range_begin: '2022-11-15T00:00:00.000-04:00',
        start_range_end: undefined,
        status: '',
        tool: '',
        search: '',
      })).toEqual({
        pipeline_key: [],
        // eslint-disable-next-line no-useless-escape
        start_range_begin: expect.stringMatching(/^2022\-11\-15T00:00:00\.000[\+\-]\d{2}:\d{2}$/),
        start_range_end: '',
        status: [],
        tool: [],
        search: '',
      });

    });

    it('should parse end date', () => {
      expect(component.remapSearchFields({
        pipeline_key: undefined,
        start_range_end: '2022-11-24T00:00:00.000-04:00',
        status: '',
        start_range_begin: '',
        tool: '',
        search: '',
      })).toEqual({
        pipeline_key: [],
        start_range_begin: '',
        // eslint-disable-next-line no-useless-escape
        start_range_end: expect.stringMatching(/^2022\-11\-24T23:59:59\.999[\+\-]\d{2}:\d{2}$/),
        status: [],
        tool: [],
        search: '',
      });

    });

    it('should trim search value', () => {
      expect(component.remapSearchFields({
        pipeline_key: undefined,
        start_range_end: '',
        status: '',
        start_range_begin: '',
        tool: '',
        search: ' test ',
      })).toEqual({
        pipeline_key: [],
        start_range_begin: '',
        start_range_end: '',
        status: [],
        tool: [],
        search: 'test',
      });

    });
  });

});
