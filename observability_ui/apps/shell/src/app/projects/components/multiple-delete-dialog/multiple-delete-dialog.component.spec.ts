import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MultipleDeleteDialogComponent } from './multiple-delete-dialog.component';
import { JourneysStore } from '../../journeys/journeys.store';
import { of } from 'rxjs';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialog, MatLegacyDialogRef } from '@angular/material/legacy-dialog';

describe('multiple-delete-dialog', () => {

  let component: MultipleDeleteDialogComponent;
  let fixture: ComponentFixture<MultipleDeleteDialogComponent>;

  let store: JourneysStore;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ MultipleDeleteDialogComponent, BrowserAnimationsModule ],
      providers: [
        MockProvider(MatLegacyDialog),
        MockProvider(MAT_LEGACY_DIALOG_DATA),
        MockProvider(MatLegacyDialogRef),
        MockProvider(JourneysStore, {
          getLoadingFor: jest.fn().mockReturnValue(of(false)),
          list$: of([]),
        })
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MultipleDeleteDialogComponent);
    component = fixture.componentInstance;

    store = TestBed.inject(JourneysStore);
    store.dispatch = jest.fn();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('getJourneysForComponent', () => {
    beforeEach(() => {
      component.data = {
        projectId: 'test-parent-id',
        ids: [],
        components: []
      };
    });

    it('should set passed component as selectedComponent', () => {
      const expected = { id: 'test-component' } as any;

      component.getJourneysForComponent(expected);
      expect(component.selectedComponent).toEqual(expected);
    });

    it('should dispatch findAll with current component as filter', () => {
      const expected = { id: 'test-component' } as any;

      component.getJourneysForComponent(expected);

      expect(store.dispatch).toHaveBeenCalledWith('findAll', {
        parentId: 'test-parent-id',
        filters: { component_id: 'test-component' }
      });
    });
  });
});
