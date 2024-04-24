import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MultipleJourneyDialogComponent } from './multiple-journey-dialog.component';
import { MockProvider } from 'ng-mocks';
import { JourneysStore } from '../../journeys/journeys.store';
import { of } from 'rxjs';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialog, MatLegacyDialogRef } from '@angular/material/legacy-dialog';

describe('multiple-journey-dialog', () => {

  let component: MultipleJourneyDialogComponent;
  let fixture: ComponentFixture<MultipleJourneyDialogComponent>;

  let store: JourneysStore;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ MultipleJourneyDialogComponent, BrowserAnimationsModule ],
      providers: [
        MockProvider(MatLegacyDialog),
        MockProvider(MAT_LEGACY_DIALOG_DATA),
        MockProvider(MatLegacyDialogRef),
        MockProvider(JourneysStore, {
          loading$: of(),
          list$: of([]),
          getLoadingFor: jest.fn().mockReturnValue(of(false)),
          dispatch: jest.fn()
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MultipleJourneyDialogComponent);
    component = fixture.componentInstance;

    store = TestBed.inject(JourneysStore);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('create journey', () => {
    beforeEach(() => {
      component.data = {
        components: [ { id: 'test-component-1' }, { id: 'test-component-2' } ],
        projectId: 'test-project-id'
      } as any;

      component.form.patchValue({
        name: 'test-name',
        description: 'test-description'
      });
    });

    it('should dispatch create journey', () => {
      component.createJourney();

      expect(store.dispatch).toHaveBeenCalledWith('createOne', {
        name: 'test-name',
        description: 'test-description',
        project_id: 'test-project-id',
        instance_rules: [],
        components: [ 'test-component-1', 'test-component-2' ]
      });
    });
  });
});
