import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { MockComponent, MockModule } from 'ng-mocks';
import { InstanceRunsComponent } from './instance-runs.component';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { FilterFieldModule } from '@observability-ui/ui';
import { TranslationModule } from '@observability-ui/translate';
import { ReactiveFormsModule } from '@angular/forms';
import { RunsModule } from '../../runs/runs.module';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { RunsStore } from '../../../stores/runs/runs.store';
import { ProjectStore, RunProcessedStatus } from '@observability-ui/core';
import { ToolSelectorComponent } from '../../integrations/tool-selector/tool-selector.component';
import { ActivatedRouteMock, Mocked, MockProvider } from '@datakitchen/ngx-toolkit';

describe('InstanceRunsComponent', () => {
  const id = '123';

  let instanceStore: Mocked<InstancesStore>;
  let runsStore: Mocked<RunsStore>;

  let component: InstanceRunsComponent;
  let fixture: ComponentFixture<InstanceRunsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InstanceRunsComponent, MockComponent(ToolSelectorComponent) ],
      imports: [
        MockModule(RunsModule),
        MockModule(TranslationModule),
        MockModule(FilterFieldModule),
        MockModule(ReactiveFormsModule)
      ],
      providers: [
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {},
              ActivatedRouteMock({ id })
            )
        },
        MockProvider(InstancesStore, class {
          components$ = of([]);
        }),
        MockProvider(RunsStore, class {
          list$ = of([]);
          getLoadingFor = () => of(false);
        }),
        MockProvider(ProjectStore, class {
          current$ = of({id: 'projectId'});
          getLoadingFor = () => of(false);
        }),
      ]
    }).compileComponents();

    instanceStore = TestBed.inject(InstancesStore) as Mocked<InstancesStore>;
    runsStore = TestBed.inject(RunsStore) as Mocked<RunsStore>;

    fixture = TestBed.createComponent(InstanceRunsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('onTableChange', () => {
    it('should next the tableChange observable', () => {
      const expected = {
        test: 'test'
      };

      component['tableChange$'].next = jest.fn();

      component.onTableChange(expected as any);

      expect(component['tableChange$'].next).toHaveBeenCalledWith(expected);
    });

    it('should fetch the new page', fakeAsync(() => {
      component.onTableChange({ pageIndex: 2, pageSize: 10, search: { component_id: null, status: null, tool: null, search: null } });
      tick();
      expect(runsStore.dispatch).toBeCalledWith('getPage', expect.objectContaining({
        page: 2,
        count: 10,
      }));
    }));

    it('should pass the filters', fakeAsync(() => {
      component.onTableChange({ pageIndex: 2, pageSize: 10, search: { component_id: '1,2', status: RunProcessedStatus.Failed, tool: 'airflow', search: ' xyz ' } });
      tick();
      expect(runsStore.dispatch).toBeCalledWith('getPage', expect.objectContaining({
        page: 2,
        count: 10,
        filters: {
          instance_id: id,
          pipeline_id: [ '1', '2' ],
          status: [ RunProcessedStatus.Failed ],
          tool: [ 'airflow' ],
          search: 'xyz'
        },
      }));
    }));

    it('should refresh header details', fakeAsync(() => {
      component.onTableChange({ pageIndex: 2, pageSize: 10, search: { component_id: null, status: null, tool: null, search: null } });
      tick();
      expect(instanceStore.dispatch).toBeCalledWith('getOne', id);
    }));
  });
});
