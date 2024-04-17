import { TestBed } from '@angular/core/testing';
import { of, ReplaySubject } from 'rxjs';
import { ComponentStore, ComponentUI } from './components.store';
import { BaseComponent, ChangedScheduleExpectation, ComponentType, Schedule } from '@observability-ui/core';
import { ComponentsService } from '../../services/components/components.service';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { TestScheduler } from '@datakitchen/rxjs-marbles';

describe('components.store', () => {
  let store: ComponentStore;
  let service: ComponentsService;
  let rxScheduler: TestScheduler;

  const getOne$ = new ReplaySubject(1);
  const getSchedules$ = new ReplaySubject(1);

  const pipeline = {
    key: 'a-key',
    name: 'name',
    display_name: 'name',
    description: 'description',
    project_id: 'project_id',
  } as BaseComponent;

  beforeEach(async () => {
    rxScheduler = new TestScheduler();

    TestBed.configureTestingModule({
      providers: [
        ComponentStore,
        MockProvider(ComponentsService, class {
          create = jest.fn().mockImplementation((entity: {
            key: string,
            name: string,
            description: string
          }, project_id: string) => {
            return of({
              key: entity.key,
              name: entity.name,
              description: entity.description,
              project_id
            } as BaseComponent);
          });
          update = (component: BaseComponent) => of(component);
          getOne = () => getOne$;
          getSchedules = () => getSchedules$;
          deleteSchedule = (id: string) => of(id);
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          createSchedule = (id: string, { changed, deleted, ...data }: ChangedScheduleExpectation) => of(data);
        }),
      ],
    });

    store = TestBed.inject(ComponentStore);
    service = TestBed.inject(ComponentsService);

    // silents console
    jest.spyOn(console, 'error').mockImplementation();
  });

  it('should exists', () => {
    expect(store).toBeTruthy();
  });

  describe('#getOne', () => {

    describe('BatchPipeline Component', () => {

      it('should add schedules to the response', () => {
        getOne$.next({ id: 'component_id', type: ComponentType.BatchPipeline });
        getSchedules$.next({
          entities: [
            { id: 'schedule_id_1', expectation: 'BATCH_PIPELINE_START_TIME' },
            { id: 'schedule_id_2', expectation: 'BATCH_PIPELINE_END_TIME' },
          ]
        });

        rxScheduler.expect$(store.getOne('id')).toContain({
          id: 'component_id',
          type: ComponentType.BatchPipeline,
          startsAt: { id: 'schedule_id_1', expectation: 'BATCH_PIPELINE_START_TIME' },
          endsAt: { id: 'schedule_id_2', expectation: 'BATCH_PIPELINE_END_TIME' },
        } as ComponentUI);
      });

    });

    describe('Dataset Component', () => {

      it('should add schedules to the response', () => {
        getOne$.next({ id: 'component_id', type: ComponentType.Dataset });
        getSchedules$.next({ entities: [ { id: 'schedule_id_1', expectation: 'DATASET_ARRIVAL' } ] });

        rxScheduler.expect$(store.getOne('id')).toContain({
          id: 'component_id',
          type: ComponentType.Dataset,
          expectedArrivalWindow: { id: 'schedule_id_1', expectation: 'DATASET_ARRIVAL' },
        } as ComponentUI);
      });

    });

    describe('all other components', () => {

      it('should only get the component', () => {
        getOne$.next({ id: 'component_id', type: ComponentType.Server });

        rxScheduler.expect$(store.getOne('id')).toContain({
          id: 'component_id',
          type: ComponentType.Server,
        } as ComponentUI);
      });

    });

  });

  describe('#create', () => {

    it('should create one', async () => {

      await store.create({
        key: 'a-key',
        name: 'name',
        description: 'description',
        type: ComponentType.BatchPipeline,
      }, 'project_id').toPromise();

      expect(service.create).toBeCalledWith({
        key: 'a-key',
        name: 'name',
        description: 'description',
        type: ComponentType.BatchPipeline,
      }, 'project_id');
    });

    it('should add create element to the list', () => {
      expect(store.onCreate({
        list: [],
        total: 0,
        all: []
      }, pipeline as BaseComponent)).toEqual({
        list: [ pipeline ],
        total: 1,
        all: [ pipeline ]
      });
    });
  });

  describe('#updateOne', () => {


    describe('when there are expectations (Batch Pipelines)', () => {

      it('should update the a component', () => {
        rxScheduler.expect$(store.updateOne({
          id: 'pipelineId',
          name: 'new name',
          description: 'Something',
          type: ComponentType.Server,
        } as BaseComponent)).toContain({
          id: 'pipelineId',
          name: 'new name',
          description: 'Something',
          type: ComponentType.Server,
        });
      });

      it('should also update expectations if argument is passed', () => {
        const startsAt = {
          margin: 300,
          schedule: 'this is a schedule',
          expectation: 'BATCH_PIPELINE_START_TIME',
        } as Schedule;

        const endsAt = {
          margin: 200,
          schedule: 'this is a schedule',
          expectation: 'BATCH_PIPELINE_END_TIME',
        } as Schedule;

        rxScheduler.expect$(store.updateOne({
          id: 'pipelineId',
          name: 'new name',
          description: 'Something',
          type: ComponentType.BatchPipeline,
        } as BaseComponent, {
          startsAt,
          endsAt,
        })).toContain({
          id: 'pipelineId',
          name: 'new name',
          description: 'Something',
          type: ComponentType.BatchPipeline,
          startsAt: {
            ...startsAt,
            timezone: undefined,
          },
          endsAt: {
            ...endsAt,
            timezone: undefined,
          },
        });

      });
    });
  });

  describe('#onUpdateOne', () => {

    it('should update selected component', () => {

      const component = { id: 'id', name: 'name' } as BaseComponent;
      expect(
        store.onUpdateOne({ list: [], total: 0, all: [] }, component)
      ).toEqual({
        list: [],
        total: 0,
        selected: component,
        all: []
      });

    });

    it('should update selected component and item in list if exists', () => {

      const component = { id: 'id', name: 'name' } as BaseComponent;
      const newComponent = { id: 'id', name: 'new name' } as BaseComponent;
      expect(
        store.onUpdateOne({ list: [ component ], total: 0, all: [] }, newComponent)
      ).toEqual({
        list: [ newComponent ],
        total: 0,
        selected: newComponent,
        all: []
      });

    });

  });

  describe('#onDeleteComponent', () => {

    const component = { id: 'id', name: 'name' } as BaseComponent;

    it('should remove the component from the list', () => {
      expect(
        store.onDeleteComponent({
          list: [ component ],
          total: 1,
          all: []
        }, { id: 'id' })
      ).toEqual({
        list: [],
        total: 0,
        all: []
      });
    });

    it('should unset selected component', () => {
      expect(
        store.onDeleteComponent({
          list: [ component ],
          total: 1,
          selected: component,
          all: []
        }, { id: 'id' })
      ).toEqual({
        list: [],
        total: 0,
        all: [],
        selected: undefined,
      });
    });
  });
});
