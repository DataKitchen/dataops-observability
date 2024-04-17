import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { BaseComponent, InstanceAlertType, JourneyDagEdge } from '@observability-ui/core';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { DagModule, DkTooltipModule } from '@observability-ui/ui';
import { MockModule } from 'ng-mocks';
import { of } from 'rxjs';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { InstanceStatusComponent } from './instance-status.component';
import { DagCompleteNode, DagStore } from '../../../stores/dag/dag.store';

describe('InstanceStatusComponent', () => {
  const instanceId = '123';
  const journeyId = '12';

  const liteNodes = [
    { info: { component: { id: '1', display_name: 'Component A' } as BaseComponent } },
    { info: { component: { id: '2', display_name: 'Component B' } as BaseComponent } },
    { info: { component: { id: '3', display_name: 'Component C' } as BaseComponent } }
  ] as DagCompleteNode[];

  const liteEdges = [
    { id: 'edge-1', from: '1', to: '3' },
    { id: 'edge-2', from: '3', to: '2' },
  ] as JourneyDagEdge[];

  let fixture: ComponentFixture<InstanceStatusComponent>;
  let component: InstanceStatusComponent;

  let store: InstancesStore;
  let dagStore: Mocked<DagStore>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InstanceStatusComponent ],
      imports: [
        MockModule(DagModule),
        MockModule(RouterModule),
        MockModule(DkTooltipModule),
      ],
      providers: [
        MockProvider(ActivatedRoute, class {
          queryParams = of({});
          snapshot = { params: {}, };
          parent = {
            params: of({ id: instanceId }),
          };
        }),
        MockProvider(InstancesStore, class {
          selected$ = of({ id: instanceId, project: { name: 'project', id: 'projectId' }, journey: { id: journeyId } });
          outOfSequenceAlert$ = of({
            id: '1',
            run: null,
            level: 'ERROR',
            type: InstanceAlertType.OutOfSequence,
            name: 'Some Alert',
            description: '',
            created_on: null,
            components: [],
          });
        } as any),
      ],
    }).overrideProvider(DagStore, {
      useFactory: () => {
        return new class {
          dispatch = jest.fn();
          nodes$ = of(liteNodes);
          edges$ = of(liteEdges);
        };
      }

    }).compileComponents();

    store = TestBed.inject(InstancesStore);

    fixture = TestBed.createComponent(InstanceStatusComponent);
    component = fixture.componentInstance;

    // Is not possible to get the component level provider using TestBed.inject
    dagStore = component['store'] as Mocked<DagStore>;

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });

  it('should fetch the DAG', () => {
    expect(component['store'].dispatch).toBeCalledWith('getDag', journeyId);
  });

  it('should get the out of sequence alert', () => {
    expect(store.dispatch).toBeCalledWith('getOutOfSequenceAlert', 'projectId', instanceId);
  });

  it('should refresh header details', () => {
    expect(store.dispatch).toBeCalledWith('getOne', instanceId);
  });

  it('should fetch individual detail for each node of the dag', () => {
    // Called one for and 3 times for the single nodes
    expect(dagStore.dispatch.mock.calls[1]).toEqual(
      [ 'getDagNodeDetail', 'projectId', instanceId, expect.anything() ],
    );
    expect(dagStore.dispatch.mock.calls[2]).toEqual(
      [ 'getDagNodeDetail', 'projectId', instanceId, expect.any(Object) ],
    );

    expect(dagStore.dispatch.mock.calls[3]).toEqual(
      [ 'getDagNodeDetail', 'projectId', instanceId, expect.any(Object) ],
    );
  });

  describe('handleError()', () => {
    it('should next the error subject', () => {
      component.handleError('something just happened');
      expect(component.error()).toEqual('something just happened');
    });
  });

  describe('resetError()', () => {
    it('should empty the error subject', () => {
      component.resetError();
      expect(component.error()).toBeUndefined();
    });
  });
});
