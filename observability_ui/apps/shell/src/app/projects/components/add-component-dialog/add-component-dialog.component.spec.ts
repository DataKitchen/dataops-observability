import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AddComponentDialogComponent } from './add-component-dialog.component';
import { MockComponent, MockComponents, MockDirective, MockModule, MockProvider } from 'ng-mocks';
import { Observable, of } from 'rxjs';
import { MatSpinner } from '@angular/material/progress-spinner';
import { ComponentType, EntityListResponse, BaseComponent, Project, ProjectStore } from '@observability-ui/core';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { EntityListPlaceholderComponent, TextFieldComponent, TextFieldErrorComponent } from '@observability-ui/ui';
import { MatTable } from '@angular/material/table';
import { ReactiveFormsModule } from '@angular/forms';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatSelect } from '@angular/material/select';
import { MatOption } from '@angular/material/core';
import { ComponentStore } from '../components.store';
import { ComponentsService } from '../../../services/components/components.service';
import { TranslationModule } from '@observability-ui/translate';
import { INTEGRATION_TOOLS } from '../../integrations/integrations.model';
import { ToolSelectorComponent } from '../../integrations/tool-selector/tool-selector.component';
import { MatLegacyDialogRef } from '@angular/material/legacy-dialog';

describe('AddComponentDialogComponent', () => {
  let component: AddComponentDialogComponent;
  let fixture: ComponentFixture<AddComponentDialogComponent>;

  let store: ComponentStore;

  const mockProject = { id: '2324', name: 'My Project' } as Project;
  const mockPipelines: BaseComponent[] = [
    { name: 'Test pipeline 1', id: '1' } as BaseComponent,
    { name: 'Test pipeline 2', id: '2' } as BaseComponent
  ];
  const mockPipelinesObservable: Observable<EntityListResponse<BaseComponent>> = of({
    entities: mockPipelines,
    total: 2,
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        MockModule(TranslationModule),
        MockModule(MatIconModule),
      ],
      declarations: [
        AddComponentDialogComponent,
        MockComponent(MatSpinner),
        MockComponent(MatIcon),
        MockComponents(TextFieldComponent, TextFieldErrorComponent),
        MockComponent(MatTable),
        MockComponent(EntityListPlaceholderComponent),
        MockComponent(MatFormField),
        MockComponent(MatSelect),
        MockComponent(MatOption),
        MockDirective(MatLabel),
        MockComponent(ToolSelectorComponent),
      ],
      providers: [
        MockProvider(ComponentsService, {
          findAll: jest.fn().mockReturnValue(mockPipelinesObservable),
          create: jest.fn().mockReturnValue(of({ name: 'Test pipeline add' })),
        }),
        MockProvider(ComponentStore, {
          dispatch: jest.fn(),
          getLoadingFor: jest.fn(),
          loading$: of({ status: true, code: 'createBatchPipeline' } as any),
          list$: of([]),
        }),
        MockProvider(MatLegacyDialogRef),
        MockProvider(ProjectStore, {
          current$: of(mockProject),
        }),
        {
          provide: INTEGRATION_TOOLS,
          useValue: [],
        }
      ]
    }).compileComponents();

    store = TestBed.inject(ComponentStore);

    fixture = TestBed.createComponent(AddComponentDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('addComponent()', () => {
    it('should create', () => {

      component.addComponent({
        type: ComponentType.BatchPipeline,
        key: 'new-pipeline',
        name: 'New Pipeline',
        description: 'description',
        tool: 'test-tool'
      });

      expect(store.dispatch).toBeCalledWith('create', {
        type: ComponentType.BatchPipeline,
        key: 'new-pipeline',
        name: 'New Pipeline',
        description: 'description',
        tool: 'test-tool'
      }, mockProject.id);
    });

  });
});
