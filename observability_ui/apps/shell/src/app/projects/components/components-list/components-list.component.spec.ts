import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ComponentsListComponent } from './components-list.component';
import { MockComponents, MockModule } from 'ng-mocks';
import { RouterTestingModule } from '@angular/router/testing';
import { MatSpinner } from '@angular/material/progress-spinner';
import { EMPTY, of } from 'rxjs';
import { Project, ProjectStore } from '@observability-ui/core';
import { MatIcon } from '@angular/material/icon';
import { MatLegacyCard as MatCard } from '@angular/material/legacy-card';
import { AddComponentDialogComponent } from '../add-component-dialog/add-component-dialog.component';
import { MockComponent } from '@datakitchen/ngx-toolkit';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ComponentStore } from '../components.store';
import { ReactiveFormsModule } from '@angular/forms';
import { TranslationModule } from '@observability-ui/translate';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { FilterFieldModule, SelectedActionsComponent } from '@observability-ui/ui';
import { QueryList } from '@angular/core';
import { MatLegacyDialog } from '@angular/material/legacy-dialog';
import { LayoutModule } from '@angular/cdk/layout';
import { MatDividerModule } from '@angular/material/divider';
import { MultipleJourneyDialogComponent } from '../multiple-journey-dialog.component.ts/multiple-journey-dialog.component';
import { MultipleDeleteDialogComponent } from '../multiple-delete-dialog/multiple-delete-dialog.component';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';

describe('ComponentsListComponent', () => {
  let component: ComponentsListComponent;
  let fixture: ComponentFixture<ComponentsListComponent>;
  let matDialog: MatLegacyDialog;
  let store: ComponentStore;
  let scheduler: TestScheduler;

  const mockProject = { id: '43221' } as Project;
  // const mockPipelines: Pipeline[] = [
  //   { name: 'Test pipeline 1', id: '1' } as Pipeline,
  //   { name: 'Test pipeline 2', id: '2' } as Pipeline
  // ];

  beforeEach(async () => {
    scheduler = new TestScheduler();

    await TestBed.configureTestingModule({
      declarations: [
        ComponentsListComponent,
        MockComponents(MatSpinner, MatIcon, MatCard, MatPaginator, SelectedActionsComponent),
        MockComponent({
          selector: 'text-field',
          inputs: [ 'formControl', 'formControlName' ],
        }),
        MockComponent({
          selector: 'breadcrumb',
          inputs: [ 'items' ],
        }),
        MockComponent({
          selector: 'shell-tool-selector',
          inputs: [ 'editing', 'tool' ],

        }),
      ],
      imports: [
        RouterTestingModule,
        MockModule(FilterFieldModule),
        MockModule(ReactiveFormsModule),
        MockModule(TranslationModule),
        MockModule(MatDividerModule),
        MockModule(LayoutModule),
      ],
      providers: [
        MockProvider(MatLegacyDialog),
        MockProvider(ProjectStore, class {
          current$ = of(mockProject);
        }),
        MockProvider(ComponentStore, class {
          list$ = of([ { id: '1', display_name: 'test', description: 'test-description' } ]);
          getLoadingFor = () => of(false);
          loading$ = of(false);
          allComponents$ = of([]);
        }),
        {
          provide: rxjsScheduler,
          useValue: scheduler,
        }
      ]
    }).compileComponents();

    matDialog = TestBed.inject(MatLegacyDialog);
    matDialog.open = jest.fn().mockImplementation(() => {
      return { afterClosed: () => EMPTY };
    });

    store = TestBed.inject(ComponentStore);

    fixture = TestBed.createComponent(ComponentsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    scheduler.flush();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get the list of components from the store', () => {
    expect(store.dispatch).toBeCalledWith('getPage', expect.objectContaining({ filters: expect.objectContaining({ component_type: [] }) }));
  });

  it('should filter by component type', () => {
    component.search.patchValue({ component_type: 'DATASET,BATCH_PIPELINE' });
    scheduler.flush();
    expect(store.dispatch).toBeCalledWith('getPage', expect.objectContaining({ filters: expect.objectContaining({ component_type: [ 'DATASET', 'BATCH_PIPELINE' ] }) }));
  });

  describe('openAddPipelineDialog', () => {
    it('should open dialog with correct parameters', () => {
      component.openAddComponentDialog();
      expect(matDialog.open).toHaveBeenCalledWith(AddComponentDialogComponent, expect.objectContaining({
        width: '500px',
        autoFocus: false
      }));
    });
  });

  describe('onCheckboxToggle', () => {
    it('should set checkbox checked to the opposite', () => {
      const checkbox = { checked: false } as any;

      component.onCheckboxToggle('test', checkbox);

      expect(checkbox.checked).toBeTruthy();
    });

    it('should add component to selectedComponents if not already selected', () => {
      const checkbox = { checked: false } as any;
      component.selectedComponents = [];

      component.onCheckboxToggle('test', checkbox);
      expect(component.selectedComponents).toEqual([ 'test' ]);
    });

    it('should remove component from selectedComponents if already selected', () => {
      const checkbox = { checked: false } as any;
      component.selectedComponents = [ 'test' ];

      component.onCheckboxToggle('test', checkbox);
      expect(component.selectedComponents).toEqual([]);
    });
  });

  describe('onClearSelection', () => {
    it('should set selected components to empty array', () => {
      component.selectedComponents = [ 'test1', 'test2', 'test3' ];
      component.onClearSelection();

      expect(component.selectedComponents).toEqual([]);
    });

    it('should set all checkboxes to unchecked', () => {
      const checkbox1 = { checked: true };
      const checkbox2 = { checked: false };
      const checkbox3 = { checked: true };

      component.checkboxes = Object.assign(new QueryList(), { _results: [ checkbox1, checkbox2, checkbox3 ] });

      component.onClearSelection();

      component.checkboxes.forEach((check) => {
        expect(check.checked).toBeFalsy();
      });
    });
  });

  describe('onSelectAll', () => {
    beforeEach(() => {
      const checkbox1 = { checked: true, value: 'test1' };
      const checkbox2 = { checked: false, value: 'test2' };
      const checkbox3 = { checked: false, value: 'test3' };

      component.checkboxes = Object.assign(new QueryList(), { _results: [ checkbox1, checkbox2, checkbox3 ] });
    });

    it('should set selected components to all checkboxes', () => {
      component.selectedComponents = [];
      component.onSelectAll();

      expect(component.selectedComponents).toEqual([ 'test1', 'test2', 'test3' ]);
    });

    it('should set all checkboxes to unchecked', () => {
      component.onSelectAll();

      component.checkboxes.forEach((check) => {
        expect(check.checked).toBeTruthy();
      });
    });
  });

  describe('showCreateJourneyDialog', () => {
    it('should open create dialog with correct parameters', () => {
      component.selectedComponents = [ 'test1', 'test2' ];
      component.parentId = 'testProject';

      component.showCreateJourneyDialog();
      expect(matDialog.open).toHaveBeenCalledWith(MultipleJourneyDialogComponent, expect.objectContaining({
        width: '600px',
        data: {
          ids: [ 'test1', 'test2' ],
          components: [],
          projectId: 'testProject'
        }
      }));
    });
  });

  describe('showMultipleDeleteDialog', () => {
    it('should open delete dialog with correct parameters', () => {
      component.selectedComponents = [ 'test1', 'test2' ];
      component.parentId = 'testProject';

      component.showMultipleDeleteDialog();
      expect(matDialog.open).toHaveBeenCalledWith(MultipleDeleteDialogComponent, expect.objectContaining({
        width: '600px',
        data: {
          ids: [ 'test1', 'test2' ],
          components: [],
          projectId: 'testProject'
        }
      }));
    });
  });
});
