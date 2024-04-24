import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AddApiKeyModalComponent } from './add-api-key-modal.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { APIKeysStore } from '../api-keys.store';
import { of } from 'rxjs';
import { ProjectStore } from '@observability-ui/core';

describe('add-api-key-modal', () => {
  const projectId = '15';

  let component: AddApiKeyModalComponent;
  let fixture: ComponentFixture<AddApiKeyModalComponent>;

  let store: APIKeysStore;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ AddApiKeyModalComponent ],
      providers: [
        MockProvider(APIKeysStore, class {
          getLoadingFor = () => of(false);
          token$ = of({});
          dispatch = jest.fn();
        }),
        MockProvider(ProjectStore, class {
          current$ = of({id: projectId});
        })
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AddApiKeyModalComponent);
    component = fixture.componentInstance;

    store = TestBed.inject(APIKeysStore);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('createKey()', () => {
    const name = 'my key';
    const expires_after_days = 1;

    beforeEach(() => {
      component.formGroup.patchValue({name, expires_after_days});
    });

    it('should send the name and expiration time to the store', () => {
      component.createKey();
      expect(store.dispatch).toBeCalledWith('create', expect.objectContaining({name, expires_after_days}), projectId);
    });

    it('should send the events api in allowed services by default', () => {
      component.createKey();
      expect(store.dispatch).toBeCalledWith('create', expect.objectContaining({allowed_services: ['EVENTS_API']}), projectId);
    });

    it('should not include the observability api in allowed services by default', () => {
      component.createKey();
      expect(store.dispatch).toBeCalledWith('create', expect.objectContaining({allowed_services: expect.not.arrayContaining(['OBSERVABILITY_API'])}), projectId);
    });

    it('should consider the form invalid if no service is allowed', () => {
      component.formGroup.patchValue({allow_send_events: false, allow_manage_components: false});
      expect(component.formGroup.valid).toBeFalsy();
    });

    it('should exclude the events api from allowed services if unchecked', () => {
      component.formGroup.patchValue({allow_send_events: false});
      component.createKey();
      expect(store.dispatch).toBeCalledWith('create', expect.objectContaining({allowed_services: expect.not.arrayContaining(['EVENTS_API'])}), projectId);
    });

    it('should include the observability api in allowed services if checked', () => {
      component.formGroup.patchValue({allow_manage_components: true});
      component.createKey();
      expect(store.dispatch).toBeCalledWith('create', expect.objectContaining({allowed_services: ['EVENTS_API', 'OBSERVABILITY_API']}), projectId);
    });
  });

});
