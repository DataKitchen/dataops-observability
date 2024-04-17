import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyDialogRef as MatDialogRef } from '@angular/material/legacy-dialog';
import { of, Subject } from 'rxjs';
import { ComponentType, Project, ProjectStore } from '@observability-ui/core';
import { ReactiveFormsModule } from '@angular/forms';
import { AddJourneyDialogComponent } from './add-journey-dialog.component';
import { JourneysActions, JourneysStore } from '../journeys.store';
import { TextFieldComponent, TextFieldErrorComponent } from '@observability-ui/ui';
import { MatFormField } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { RouterTestingModule } from '@angular/router/testing';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { MockComponents, MockModule } from 'ng-mocks';
import { LoadingState } from '@microphi/store';
import { Router } from '@angular/router';
import { JourneysService } from '../../../services/journeys/journeys.service';
import { ComponentsService } from '../../../services/components/components.service';
import { JourneyInstanceRulesComponent } from '../journey-instance-rules/journey-instance-rules.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { Journey, JourneyInstanceRule } from '@observability-ui/core';

describe('AddJourneyDialogComponent', () => {
  let component: AddJourneyDialogComponent;
  let fixture: ComponentFixture<AddJourneyDialogComponent>;

  let store: Mocked<JourneysStore>;
  let componentsService: Mocked<ComponentsService>;
  let dialog: Mocked<MatDialogRef<any>>;
  let router: Router;

  const loadingState$ = new Subject<LoadingState<JourneysActions>>();

  const mockRules = [
    {action: 'START', batch_pipeline: '1'},
    {action: 'END', batch_pipeline: '2'},
  ] as JourneyInstanceRule[];
  const mockProject = { id: '2324', name: 'My Project' } as Project;
  const mockJourney = { id: '123', name: 'My New Journey', instance_rules: mockRules } as Journey;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        RouterTestingModule,
        MockModule(MatExpansionModule),
      ],
      declarations: [
        AddJourneyDialogComponent,
        MockComponents(TextFieldComponent, TextFieldErrorComponent, MatFormField, MatIcon, JourneyInstanceRulesComponent),
      ],
      providers: [
        MockProvider(JourneysStore, class {
          loading$ = loadingState$;
          list$ = of([]);
        }),
        MockProvider(MatDialogRef),
        MockProvider(JourneysService, class {
          createJourneyDagEdge = jest.fn().mockImplementation(() => of({}));
        }),
        MockProvider(ComponentsService),
        MockProvider(ProjectStore, class {
          current$ = of(mockProject);
        }),
      ]
    }).compileComponents();

    store = TestBed.inject(JourneysStore) as Mocked<JourneysStore>;
    componentsService = TestBed.inject(ComponentsService) as Mocked<ComponentsService>;
    dialog = TestBed.inject(MatDialogRef) as Mocked<MatDialogRef<any>>;
    router = TestBed.inject(Router);

    jest.spyOn(router, 'navigate').mockImplementation();

    fixture = TestBed.createComponent(AddJourneyDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should fetch all the components for the project', () => {
    expect(componentsService.findAll).toBeCalledWith({ parentId: mockProject.id, filters: {component_type: [ ComponentType.BatchPipeline ]} });
  });

  describe('addJourney()', () => {

    it('should dispatch the event', () => {
      component.addJourney({ name: 'New Journey', description: 'description', instance_rules: mockRules });
      expect(store.dispatch).toBeCalledWith('createOne', { name: 'New Journey', description: 'description', instance_rules: mockRules, project_id: mockProject.id });
    });


    describe('on failure', () => {
      beforeEach(() => {
        loadingState$.next({
          code: 'createOne',
          error: 'my awesome error',
          status: false,
        });

      });

      it('should show error', () => {

        expect(component.error).toEqual('my awesome error');
      });

    });

    describe('on success', () => {
      beforeEach(() => {
        loadingState$.next({
          code: 'createOne',
          response: mockJourney,
          status: false,
        });
      });


      it('should close the dialog when adding a new journey success', () => {

        expect(dialog.close).toHaveBeenCalled();
      });

      it('should redirect to newly created journey page', () => {
        expect(router.navigate).toHaveBeenCalledWith([ mockJourney.id ], expect.anything());
      });
    });


  });

});
