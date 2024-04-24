import { TestBed } from '@angular/core/testing';
import { JourneysStore } from './journeys.store';
import { JourneysService } from '../../services/journeys/journeys.service';
import { Journey, JourneyInstanceRule } from '@observability-ui/core';
import { BaseComponent, ComponentType } from '@observability-ui/core';
import { of } from 'rxjs';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';

describe('journeys.store', () => {
  const journeyId = 'journey-id';
  const journey = { name: 'journey', project: 'project_id', instance_rules: [] as JourneyInstanceRule[] } as Journey;

  const components = [ {
    created_on: '2022-10-30T13:55:18+00:00',
    display_name: 'Update_Monitor_to_Handle_Resume.Utility_Monitor_Events.Test_Monitor',
    id: '01ae859c-1a67-40bb-8444-a0a6dbb5e8d4',
    key: 'Update_Monitor_to_Handle_Resume.Utility_Monitor__Events.Test_Monitor',
    project_id: '6238a101-74e0-4edb-93c6-994da8fa2c2d',
    type: 'BATCH_PIPELINE',
    active: true,
  },
    {
      created_on: '2022-10-30T13:55:18+00:00',
      display_name: 'Update_Monitor_to_Handle_Resume.Utility_Monitor_Events.Test_Monitor_Minimal',
      id: '82dc1fe0-d6cb-4960-8ed3-ded8ef963ffc',
      key: 'Update_Monitor_to_Handle_Resume.Utility_Monitor_Events.Test_Monitor_Minimal',
      project_id: '6238a101-74e0-4edb-93c6-994da8fa2c2d',
      type: 'BATCH_PIPELINE',
      active: true
    } ] as BaseComponent[];

  let store: JourneysStore;
  let service: Mocked<JourneysService>;

  let scheduler: TestScheduler;


  beforeEach(async () => {
    scheduler = new TestScheduler();

    TestBed.configureTestingModule({
      providers: [
        JourneysStore,
        MockProvider(JourneysService, class {
          getOne = () => of(journey);
          createInstanceRule = jest.fn().mockImplementation((e) => of(e));
          deleteInstanceRule = jest.fn().mockReturnValue(of({}));
          getComponentsByJourney = jest.fn().mockReturnValue(of({ entities: components, total: components.length }));
          createJourneyDagEdge = jest.fn().mockReturnValue(of(true));

          create(entity: Journey, parentId?: string) {
            return of({
              name: entity.name,
              description: entity.description,
              instance_rules: entity.instance_rules,
              project: parentId,
            });
          }

          update({ id, ...entity }: Partial<Journey>) {
            return of({
              id,
              name: entity.name,
              description: entity.description,
              instance_rules: entity.instance_rules,
            });
          }
        })
      ],
    });

    store = TestBed.inject(JourneysStore);
    service = TestBed.inject(JourneysService) as Mocked<JourneysService>;
    // silents console
    jest.spyOn(console, 'error').mockImplementation();
  });

  it('should exists', () => {
    expect(store).toBeTruthy();
  });

  describe('#createOne', () => {
    it('should create one', () => {
      scheduler.expect$(store.createOne({
        name: 'name',
        description: 'description',
        instance_rules: [],
        project_id: 'project_id',
      })).toContain({
        name: 'name',
        description: 'description',
        project: 'project_id',
      } as Journey);

    });

    it('should add create element to the list', () => {
      expect(store.onCreateOne({
        list: [], total: 0, components: []
      }, journey as Journey)).toEqual({
        list: [ journey ],
        total: 1,
        components: []
      });
    });

    it('should add components if there are components', (done) => {
      store.createOne({
        components: [ 'test1', 'test2' ],
        name: 'test',
        description: 'test',
        instance_rules: [],
        project_id: 'testProject'
      }).subscribe(() => {
        expect(service.createJourneyDagEdge).toHaveBeenCalledTimes(2);
        done();
      });
    });
  });

  describe('#updateOne', () => {
    it('should update the journey', () => {
      scheduler.expect$(store.updateOne({
        id: journeyId,
        name: 'name',
        description: 'Something',
        instance_rules: [],
      })).toContain({
        id: 'journey-id',
        name: 'name',
        description: 'Something',
      });
    });

    it('should updated selected', () => {
      const baseState = {
        list: [ { ...journey, id: journeyId } ],
        total: 1,
        components: [] as any[],
      };
      expect(store.onUpdateOne(baseState, { ...journey, id: journeyId, description: 'updated' })).toEqual({
        ...baseState,
        selected: {
          ...journey,
          id: journeyId,
          description: 'updated'
        },
      });
    });

    it('should log an error if updating journey not in the store', () => {
      const baseState = {
        list: [] as any[],
        total: 0,
        components: [] as any[],
      };


      jest.spyOn(global.console, 'error');
      store.onUpdateOne(baseState, { ...journey, id: journeyId });

      expect(global.console.error).toBeCalledWith(expect.any(String));
    });

    it('should update the store with the updated journey', () => {
      const baseState = {
        list: [ { ...journey, id: journeyId } ],
        total: 1,
        components: [] as any[]
      };
      expect(store.onUpdateOne(baseState, {
        ...journey,
        name: 'New Name' as any,
        id: journeyId
      }))
        .toEqual(expect.objectContaining({ list: expect.arrayContaining([ expect.objectContaining({ name: 'New Name' }) ]) }));
    });

  });

  describe('#findComponents', () => {

    it('should get all components', () => {
      scheduler.expect$(store.findComponents('id')).toContain(components);
    });

    it('should get all filtered components ', (done) => {
      store.findComponents('id', { component_type: [ ComponentType.BatchPipeline ] }).subscribe(() => {
        expect(service.getComponentsByJourney).toBeCalledWith('id', { component_type: [ ComponentType.BatchPipeline ] });
        done();
      });
    });

    it('should reduce', () => {
      const baseState = {
        list: [ { ...journey, id: journeyId } ],
        total: 1,
        components: [] as any[],
      };

      expect(store.onFindComponents(baseState, components)).toEqual({
        ...baseState,
        components: components,
      });
    });
  });
});
