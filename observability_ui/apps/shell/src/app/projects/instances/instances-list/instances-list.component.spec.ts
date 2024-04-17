import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockComponent, MockComponents, MockDirective, MockModule } from 'ng-mocks';
import { of } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { MatSpinner } from '@angular/material/progress-spinner';
import { Project, ProjectStore } from '@observability-ui/core';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { MatPaginator } from '@angular/material/paginator';
import { BreadcrumbModule, EntityListPlaceholderComponent, FilterFieldModule, TableWrapperComponent } from '@observability-ui/ui';
import { MatHeaderRow, MatHeaderRowDef, MatRow, MatRowDef, MatTable } from '@angular/material/table';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { InstancesListComponent } from './instances-list.component';
import { Instance } from '@observability-ui/core';
import { JourneysService } from '../../../services/journeys/journeys.service';
import { InstancesService } from '../../../services/instances/instances.service';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { TranslationModule } from '@observability-ui/translate';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { InstanceAlertsComponent } from '../instance-alerts/instance-alerts.component';
import { MatLegacyDialog } from '@angular/material/legacy-dialog';
import { TestScheduler } from '@datakitchen/rxjs-marbles';

describe('InstancesListComponent', () => {
  let component: InstancesListComponent;
  let fixture: ComponentFixture<InstancesListComponent>;
  let service: InstancesService;

  const mockedInstances: Instance[] = [
    {
      id: '1',
      journey: 'Sales Tableau Reporting',
      start_time: '2023-01-01T17:08:02',
      end_time: '2023-01-02T17:08:02'
    } as any,
    { id: '2', journey: 'Marketing Lead Generations', start_time: '2022-01-01T17:08:02' } as any,
  ];
  const mockProject = { id: '342', name: 'My Project' } as Project;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        InstancesListComponent,
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
        MockDirective(MatLabel)
      ],
      imports: [
        MockModule(ReactiveFormsModule),
        MockModule(MatDatepickerModule),
        MockModule(FilterFieldModule),
        MockModule(MatFormFieldModule),
        MockModule(BreadcrumbModule),
        MockModule(TranslationModule),
        InstanceAlertsComponent
      ],
      providers: [
        MockProvider(InstancesService),
        MockProvider(StorageService),
        MockProvider(ParameterService),
        MockProvider(MatLegacyDialog),
        MockProvider(JourneysService, class {
          findAll = () => of({
            entities: [
              { name: 'cage' },
              { name: 'zero' },
              { name: 'beauty' },
            ],
          });
        }),
        MockProvider(ActivatedRoute, class {
          params = of({ projectId: 15 });
          snapshot: {
            params: {
              projectId: 1
            }
          };
        }),
        MockProvider(ProjectStore, class {
          current$ = of(mockProject);
        }),
        MockProvider(InstancesStore, class {
          list$ = of([]);
          total$ = of(0);
          getLoadingFor = () => of(false);
        }),
      ],
    }).compileComponents();

    service = TestBed.inject(InstancesService);
    service.getPage = jest.fn().mockReturnValue(of(mockedInstances));

    fixture = TestBed.createComponent(InstancesListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should provide journey names sorted', () => {
    TestScheduler.expect$(component.allJourneys$).toContain([
      expect.objectContaining({ name: 'beauty' }),
      expect.objectContaining({ name: 'cage' }),
      expect.objectContaining({ name: 'zero' }),
    ]);
  });

  describe('#remapSearchFields', () => {

    it('should be defensive', () => {
      expect(component.remapSearchFields({
        // @ts-ignore
        journey_id: undefined,
        start_range_begin: undefined,
        start_range_end: undefined,
        active: undefined,
        search: undefined
      })).toEqual({
        journey_id: [],
        start_range_begin: '',
        start_range_end: '',
      });
    });

    it('should send empty if active and ended are both selected', () => {
      expect(component.remapSearchFields({
        // @ts-ignore
        journey_id: undefined,
        start_range_begin: undefined,
        start_range_end: undefined,
        active: 'true,false',
        search: undefined
      })).toEqual({
        journey_id: [],
        start_range_begin: '',
        start_range_end: '',
        active: ''
      });
    });

    it('should send true if active is selected', () => {
      expect(component.remapSearchFields({
        // @ts-ignore
        journey_id: undefined,
        start_range_begin: undefined,
        start_range_end: undefined,
        active: 'true',
        search: undefined
      })).toEqual({
        journey_id: [],
        start_range_begin: '',
        start_range_end: '',
        active: 'true'
      });
    });

    it('should send false if ended is selected', () => {
      expect(component.remapSearchFields({
        // @ts-ignore
        journey_id: undefined,
        start_range_begin: undefined,
        start_range_end: undefined,
        active: 'false',
        search: undefined
      })).toEqual({
        journey_id: [],
        start_range_begin: '',
        start_range_end: '',
        active: 'false'
      });
    });

    it('should remove empty names', () => {
      expect(component.remapSearchFields({
        // @ts-ignore
        journey_id: 'hello,,mr,me',
        start_range_begin: undefined,
        start_range_end: undefined,
        active: undefined,
        search: undefined
      })).toEqual({
        journey_id: [ 'hello', 'mr', 'me' ],
        start_range_begin: '',
        start_range_end: '',
      });
    });

    it('should parse start date', () => {
      expect(component.remapSearchFields({
        journey_id: undefined,
        start_range_begin: '2022-11-15T00:00:00.000-04:00',
        start_range_end: undefined,
        active: '', search: undefined
      })).toEqual({
        journey_id: [],
        // eslint-disable-next-line no-useless-escape
        start_range_begin: expect.stringMatching(/^2022\-11\-15T00:00:00\.000[\+\-]\d{2}:\d{2}$/),
        start_range_end: '',
        active: '',
      });

    });

    it('should parse end date', () => {
      expect(component.remapSearchFields({
        journey_id: undefined,
        start_range_end: '2022-11-24T00:00:00.000-04:00',
        start_range_begin: undefined,
        active: '',
        search: undefined
      })).toEqual({
        journey_id: [],
        start_range_begin: '',
        // eslint-disable-next-line no-useless-escape
        start_range_end: expect.stringMatching(/^2022\-11\-24T23:59:59\.999[\+\-]\d{2}:\d{2}$/),
        active: ''
      });

    });
  });

});
