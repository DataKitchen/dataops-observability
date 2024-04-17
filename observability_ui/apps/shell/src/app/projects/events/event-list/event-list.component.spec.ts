import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EventListComponent } from './event-list.component';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { ComponentStore } from '../../components/components.store';
import { ProjectStore } from '@observability-ui/core';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { RouterTestingModule } from '@angular/router/testing';
import { MockComponent } from 'ng-mocks';
import { FilterFieldModule } from '@observability-ui/ui';
import { TranslatePipeMock } from '@observability-ui/translate';
import { EventsTableComponent } from '../../runs/events-table/events-table.component';
import { of } from 'rxjs';
import { ReactiveFormsModule } from '@angular/forms';

describe('event-list', () => {

  let component: EventListComponent;
  let fixture: ComponentFixture<EventListComponent>;

  let store: Mocked<ProjectStore>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        FilterFieldModule,
        ReactiveFormsModule,
      ],
      declarations: [
        EventListComponent,
        TranslatePipeMock,
        MockComponent(EventsTableComponent),
      ],
      providers: [
        MockProvider(ComponentStore, class {
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        }),
        MockProvider(ProjectStore, class {
          current$ = of({ id: 'project_id' });
          getLoadingFor = jest.fn().mockReturnValue(of(false));
        }),
        MockProvider(ParameterService),
        MockProvider(StorageService),
        // ActivatedRouteMock({}),

      ]
    }).compileComponents();

    store = TestBed.inject(ProjectStore) as Mocked<ProjectStore>;

    fixture = TestBed.createComponent(EventListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('onTableChange()', () => {
    it('should pass the filters to the store', () => {
      component.onTableChange({ pageIndex: 0, pageSize: 10, search: { event_type: 'A,B', component_id: '1,2' } });
      expect(store.dispatch).toBeCalledWith('getEventsByPage', expect.objectContaining({
        parentId: 'project_id',
        count: 10,
        page: 0,
        filters: {
          event_type: [ 'A', 'B' ],
          component_id: [ '1', '2' ],
        }
      }));
    });
  });
});
