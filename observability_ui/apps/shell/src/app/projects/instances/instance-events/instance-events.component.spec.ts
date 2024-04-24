import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { of } from 'rxjs';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MockComponent, MockModule } from 'ng-mocks';
import { FilterFieldModule, TableWrapperComponent } from '@observability-ui/ui';
import { mockRunEvents } from '../../../services/run-events/run-events.mock';
import { ConfigService, EventType, BaseComponent, ProjectStore } from '@observability-ui/core';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { ActivatedRoute } from '@angular/router';
import { InstanceEventsComponent } from './instance-events.component';
import { TranslationModule } from '@observability-ui/translate';
import { ReactiveFormsModule } from '@angular/forms';
import { RunsModule } from '../../runs/runs.module';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { InstancesStore } from '../../../stores/instances/instances.store';

describe('InstanceEventsComponent', () => {
  const instanceId = '1';
  const instance = {id: instanceId, journey: {id: '12', name: ''}};
  const events = mockRunEvents;
  const components = [ { display_name: 'A' }, { display_name: 'B' }, { display_name: 'C' } ] as BaseComponent[];

  let projectStore: Mocked<ProjectStore>;
  let instanceStore: Mocked<InstancesStore>;

  let component: InstanceEventsComponent;
  let fixture: ComponentFixture<InstanceEventsComponent>;

  beforeEach(async () => {

    await TestBed.configureTestingModule({
      declarations: [
        InstanceEventsComponent,
        MockComponent(TableWrapperComponent),
      ],
      imports: [
        HttpClientTestingModule,
        MockModule(RunsModule),
        MockModule(TranslationModule),
        MockModule(FilterFieldModule),
        MockModule(ReactiveFormsModule)
      ],
      providers: [
        MockProvider(InstancesStore, class {
          components$ = of(components);
          getEntity = () => of(instance);
        }),
        MockProvider(ProjectStore, class {
          events$ = of(events as unknown as EventType[]);
          totalEvents$ = of(events.length);
          current$ = of({id: 'projectId'});
          getLoadingFor = () => of(false);
        }),
        MockProvider(ParameterService),
        MockProvider(StorageService),
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {},
              ActivatedRouteMock({ id : '1'})
            )
        },
      ]
    }).compileComponents();

    instanceStore = TestBed.inject(InstancesStore) as Mocked<InstancesStore>;
    projectStore = TestBed.inject(ProjectStore) as Mocked<ProjectStore>;

    fixture = TestBed.createComponent(InstanceEventsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should set a filters storage key', () => {
    expect(component.storageKey).toBe(`1:InstanceEvents:`);
  });

  it('should get all tasks for the run', () => {
    expect(instanceStore.dispatch).toBeCalledWith('findComponents', instance.journey.id);
  });

  describe('onTableChange', () => {
    it('should fetch the new page', fakeAsync(() => {
      component.onTableChange({ pageIndex: 2, pageSize: 10, search: {} });
      tick();
      expect(projectStore.dispatch).toBeCalledWith('getEventsByPage', expect.objectContaining({
        parentId: "projectId",
        page: 2,
        count: 10,
      }));
    }));

    it('should pass the filters', fakeAsync(() => {
      component.onTableChange({ pageIndex: 2, pageSize: 10, search: {component_id: '1,2', event_type: 'A,B'} });
      tick();
      expect(projectStore.dispatch).toBeCalledWith('getEventsByPage', expect.objectContaining({
        parentId: "projectId",
        page: 2,
        count: 10,
        filters: {
          instance_id: instanceId,
          component_id: [ '1', '2' ],
          event_type: [ 'A', 'B' ],
        },
      }));
    }));

    it('should refresh header details', fakeAsync(() => {
      component.onTableChange({ pageIndex: 2, pageSize: 10, search: {} });
      tick();
      expect(instanceStore.dispatch).toBeCalledWith('getOne', instanceId);
    }));
  });
});
