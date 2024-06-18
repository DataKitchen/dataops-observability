import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SettingsComponent } from './settings.component';
import { MockProvider } from 'ng-mocks';
import { Company, EntitiesResolver, Project, ProjectStore } from '@observability-ui/core';
import { of } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('Settings', () => {
  let fixture: ComponentFixture<SettingsComponent>;
  let component: SettingsComponent;

  let store: ProjectStore;
  let dialog: MatDialog;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ SettingsComponent, NoopAnimationsModule ],
      providers: [ MockProvider(MatDialog), MockProvider(ProjectStore, {
        current$: of({ id: '1', name: 'current' } as Project),
        getLoadingFor: jest.fn().mockReturnValue(of(false))
      }), MockProvider(EntitiesResolver, {
        company$: of({ id: '2', name: 'company' } as Company)
      }) ]
    });

    store = TestBed.inject(ProjectStore);
    store.dispatch = jest.fn();

    dialog = TestBed.inject(MatDialog);
    dialog.open = jest.fn();

    fixture = TestBed.createComponent(SettingsComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('saveInfo', () => {
    it('should dispatch updateOne', () => {
      component.saveInfo();
      expect(store.dispatch).toHaveBeenCalled();
    });
  });

  describe('cancelInfoChanges', () => {
    it('should patch form with initial values', () => {
      component.form.patchValue({
        name: 'changed-test-name',
        description: 'changed-test-description'
      });

      component.cancelInfoChanges({ name: 'original-name', description: 'original-description' } as any);
      expect(component.form.value).toEqual(expect.objectContaining({
        name: 'original-name',
        description: 'original-description'
      }));
    });
  });
});
