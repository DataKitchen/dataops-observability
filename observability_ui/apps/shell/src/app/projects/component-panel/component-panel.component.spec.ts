import { ComponentPanelComponent } from './component-panel.component';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockComponent, MockModule, MockProvider, MockProviders } from 'ng-mocks';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BehaviorSubject, of } from 'rxjs';
import { TranslationModule } from '@observability-ui/translate';
import { MatExpansionModule } from '@angular/material/expansion';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { MatIconModule } from '@angular/material/icon';
import { BaseComponent, ComponentType, ProjectStore } from '@observability-ui/core';
import { ComponentStore } from '../components/components.store';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { LoadingState } from '@microphi/store';
import { Mocked } from '@datakitchen/ngx-toolkit';
import { JourneysStore } from '../journeys/journeys.store';
import { ComponentsService } from '../../services/components/components.service';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { CreatedByComponent } from '@observability-ui/ui';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { ToolSelectorComponent } from '../integrations/tool-selector/tool-selector.component';
import { GetToolClassPipe } from '../integrations/tool-selector/get-tool-class.pipe';
import { DagStore } from '../../stores/dag/dag.store';

// @ts-ignore
window.matchMedia = window.matchMedia || function() {
  return {
    matches: false,
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    addListener: function() {
    },
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    removeListener: function() {
    }
  };
};

describe('ComponentPanelComponent', () => {
  const project = { id: '15' };
  const pipeline = {
    id: '1',
    type: ComponentType.StreamingPipeline,
    key: 'component-key',
    name: 'Component Name',
    display_name: 'Component Name',
    description: 'component description',
    tool: 'my-tool',
  } as BaseComponent;

  let componentsStore: Mocked<ComponentStore>;
  let dagStore: Mocked<DagStore>;
  let loadingAction$: BehaviorSubject<LoadingState<ComponentStore>>;

  let component: ComponentPanelComponent;
  let fixture: ComponentFixture<ComponentPanelComponent>;

  beforeEach(async () => {
    loadingAction$ = new BehaviorSubject({} as LoadingState<ComponentStore>);

    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        NoopAnimationsModule,
        MockModule(TranslationModule),
        MockModule(MatExpansionModule),
        MockModule(ReactiveFormsModule),
        MockModule(MatProgressSpinnerModule),
        MockModule(MatDialogModule),
        MockModule(MatIconModule),
        GetToolClassPipe,
      ],
      declarations: [
        ComponentPanelComponent,
        MockComponent(CreatedByComponent),
        MockComponent(ComponentIconComponent),
        MockComponent(ToolSelectorComponent),
      ],
      providers: [
        MockProviders(MatSnackBar),
        MockProvider(ComponentsService, {
          getOne: jest.fn().mockReturnValue(of(pipeline))
        }),
        MockProvider(ComponentStore, {
          dispatch: jest.fn(),
          loading$: loadingAction$,
          selected$: of(pipeline),
          getLoadingFor: () => of(false),
        } as any),
        MockProvider(DagStore, {
          dispatch: jest.fn(),
        } as any),
        MockProvider(JourneysStore, {
          dispatch: jest.fn()
        }),
        MockProvider(ProjectStore, {
          current$: of(project),
        } as any),
        MockProvider(MatDialog)
      ],
    }).compileComponents();

    jest.spyOn(console, 'warn').mockImplementation();

    componentsStore = TestBed.inject(ComponentStore) as Mocked<ComponentStore>;
    dagStore = TestBed.inject(DagStore) as Mocked<DagStore>;

    fixture = TestBed.createComponent(ComponentPanelComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();

    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('patching the form', () => {

    it('should set default values', () => {
      // display_name is not part of the form
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { display_name, ...comp } = pipeline;

      expect(component.form.value).toEqual({
        ...comp,
        startsAt: null,
        endsAt: null,
        expectedArrivalWindow: null,
      });
    });
  });


  it('should catch the error message on update', () => {
    const error = new Error('something bad just happened');
    new TestScheduler().run(({ expectObservable }) => {
      loadingAction$.next({ code: 'updateOne', status: false, error });
      expectObservable(component.error$).toBe('a', { a: error.message });
    });
  });

  it('should set editing to false after done updating', () => {
    component.editing$.next(true);
    new TestScheduler().run(({ flush }) => {
      loadingAction$.next({ code: 'updateOne', status: false });
      flush();
      expect(component.editing$.getValue()).toBeFalsy();
    });
  });

  describe('setEditing()', () => {
    it('should next true to the editing subject', () => {
      component.setEditing(true);
      expect(component.editing$.getValue()).toBeTruthy();
    });

    it('should next false to the editing subject', () => {
      component.setEditing(false);
      expect(component.editing$.getValue()).toBeFalsy();
    });
  });

  describe('save()', () => {
    it('should update the component', () => {
      setTimeout(() => {
        component.save();
        expect(componentsStore.dispatch).toBeCalledWith('updateOne', pipeline, expect.anything(), expect.anything());
      }, 200);
    });

    it('should notify the journey relationships store about the update', () => {
      const newName = 'New Component Name';
      component.form.patchValue({ name: newName });

      component.save();

      expect(dagStore.dispatch).toBeCalledWith('updateNodeInfo', {
        ...pipeline,
        name: newName,
        display_name: newName
      });
    });
  });
});
