import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeleteKeyModalComponent } from './delete-key-modal.component';
import { MockProvider } from 'ng-mocks';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialogRef } from '@angular/material/legacy-dialog';
import { APIKeysStore } from '../api-keys.store';
import { of } from 'rxjs';

describe('delete keys modal', () => {
  let component: DeleteKeyModalComponent;
  let fixture: ComponentFixture<DeleteKeyModalComponent>;

  let store: APIKeysStore;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ DeleteKeyModalComponent ],
      providers: [
        MockProvider(MAT_LEGACY_DIALOG_DATA),
        MockProvider(MatLegacyDialogRef),
        MockProvider(APIKeysStore, {
          getLoadingFor: jest.fn().mockReturnValue(of(false)),
          loading$: of()
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DeleteKeyModalComponent);
    component = fixture.componentInstance;

    store = TestBed.inject(APIKeysStore);
    store.dispatch = jest.fn();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('deleteSelected', () => {
    it('should dispatch the deleteAction for each id', () => {
      component.data = { ids: [ 'test1', 'test2', 'test3' ] };

      component.deleteSelected();

      expect(store.dispatch).toHaveBeenCalledTimes(3);
    });
  });
});
