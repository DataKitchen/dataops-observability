import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MultipleComponentPanelComponent } from './multiple-component-panel.component';
import { Schedule } from '@observability-ui/core';
import { MockProvider } from 'ng-mocks';
import { ComponentStore } from '../components/components.store';
import { of } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { MatExpansionModule } from '@angular/material/expansion';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('MultipleComponentPanel', () => {
  let fixture: ComponentFixture<MultipleComponentPanelComponent>;
  let component: MultipleComponentPanelComponent;

  let store: ComponentStore;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [
        MockProvider(ActivatedRoute, {
          snapshot: {
            params: {
              ids: 'test-component-1,test-component-2,test-component-3'
            }
          } as any
        }),
        MockProvider(ComponentStore, {
          getLoadingFor: jest.fn().mockReturnValue(of(false)),
          allComponents$: of([
            { id: 'test-component-1' } as any,
            { id: 'test-component-2' } as any,
            { id: 'test-component-3' } as any
          ]),
          loading$: of(),
          updateOne: jest.fn(),
          dispatch: jest.fn()
        })
      ],
      imports: [
        MultipleComponentPanelComponent,
        MatExpansionModule,
        NoopAnimationsModule
      ],
    });

    store = TestBed.inject(ComponentStore);

    fixture = TestBed.createComponent(MultipleComponentPanelComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });

  describe('save', () => {
    beforeEach(() => {
      component.form.patchValue({
        editArrival: true,
        editTool: true,
        editSchedule: true,
        tool: 'test-tool',
        expectedArrivalWindow: { schedule: '0 1 */2 * *', timezone: 'America/New_York' } as Schedule
      });
    });

    it('should call updateOne for each component', () => {
      component.save();
      expect(store.dispatch).toHaveBeenCalledTimes(3);
    });
  });
});
