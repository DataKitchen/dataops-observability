import { AlertsDialogComponent } from './alerts-dialog.component';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA } from '@angular/material/legacy-dialog';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { of } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';

describe('Alerts Dialog Component', () => {
  let component: AlertsDialogComponent;
  let fixture: ComponentFixture<AlertsDialogComponent>;

  let store: InstancesStore;
  let testScheduler: TestScheduler;

  beforeEach(async () => {
    testScheduler = new TestScheduler();

    await TestBed.configureTestingModule({
      imports: [ AlertsDialogComponent ],
      providers: [
        {
          provide: rxjsScheduler,
          useValue: testScheduler,
        },
        MockProvider(ActivatedRoute, {
          queryParams: of({})
        }),
        MockProvider(MAT_DIALOG_DATA, {
          projectId: 1,
          instanceId: 1,
          instance: {}
        }),
        MockProvider(InstancesStore, {
          getLoadingFor: jest.fn().mockReturnValue(of(false)),
          instanceAlerts$: of([]),
          instanceAlertsTotal$: of(0),
          components$: of([]),
        })
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AlertsDialogComponent);
    component = fixture.componentInstance;

    store = TestBed.inject(InstancesStore);
    store.dispatch = jest.fn();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('onTableChange', () => {
    it('should next tableChange subject', () => {
      component.tableChange$.next = jest.fn();

      const expected = {
        pageIndex: 1,
        pageSize: 2,
        search: {
          component_id: 'test'
        }
      };

      component.onTableChange(expected);

      expect(component.tableChange$.next).toHaveBeenCalledWith(expected);
    });
  });

  describe('tableChange$', () => {
    it('should get the alerts from the store', () => {
      testScheduler.run(({ flush }) => {
        component.tableChange$.next({
          pageIndex: 1,
          pageSize: 2,
          search: {
            component_id: 'test'
          }
        });
        flush();
        expect(store.dispatch).toBeCalledWith('getAlertsByPage', 1, 1, {
          count: 2,
          page: 1,
          sort: 'desc',
          filters:
            {
              component_id: [
                'test',
              ],
              type: [],
            }
        });
      });
    });
  });
});
