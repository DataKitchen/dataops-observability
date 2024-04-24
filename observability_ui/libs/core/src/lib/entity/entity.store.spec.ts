import { Entity, EntityListResponse, Pagination, SortOptions, WithId } from './entity.model';
import { EntityActions, EntityState, EntityStore, entityStoreInitialState } from './entity.store';
import { Observable, of } from 'rxjs';
import { Injectable } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MockProvider } from 'ng-mocks';
import { ConfigService } from '../config/config.service';
import { Reduce } from '@microphi/store';
import { EntityService } from './entity.service';
import { EntityType } from './entity-type';
import { TestScheduler } from '@datakitchen/rxjs-marbles';

describe('entity.store', () => {


  interface Ent extends WithId {
    type: 'animal' | 'plant';
  }

  type EntState = EntityState<Ent>;

  interface EntActions extends EntityActions<Ent> {
    getAnimals: () => Observable<Ent[]>;
    getPlants: () => Observable<Ent[]>;
  }

  @Injectable()
  class EntService extends EntityService<Ent> {
    protected override readonly path: string = 'v1';
    protected override readonly prefix: string = 'prefix';
    protected readonly baseEntity = EntityType.Company;
  }


  @Injectable()
  class EntStore extends EntityStore<EntState, EntActions> {
    constructor(protected service: EntService) {
      super({
        list: [{ id: 'a1', type: 'animal'}],
        total: 1
      });
    }

    @Reduce()
    override onGetPage(state: EntState, payload: EntityListResponse<EntState extends EntityState<infer Ent> ? Ent : Entity> & Pagination & SortOptions): EntState {
      const s = super.onGetPage(state, payload);
      return {
        ...s,
      };
    }
  }

  let service: EntService;
  let store: EntStore;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
      ],
      providers: [
        EntStore,
        EntService,
        // @ts-ignore
        MockProvider(ConfigService, {
          get: () => 'base'
        })
      ],
    }).compileComponents();

    service = TestBed.inject(EntService);
    store = TestBed.inject(EntStore);
    http = TestBed.inject(HttpTestingController);
  });

  it('should create', () => {
    expect(store).toBeTruthy();
    expect(service).toBeTruthy();
  });

  describe('#getEntity', () => {
    it('should get an entity if exists', () => {
      new TestScheduler().expectObservable(store.getEntity('a1')).toEqual(of({id: 'a1', type: 'animal'}));
    });

    it('should be defensive', () => {
      new TestScheduler().expectObservable(store.getEntity('a2')).toEqual(of(undefined));
    });
  });

  describe('#getOne', () => {
    it('should get an entity (effect)', (done) => {

      store.getOne('a2').subscribe((resp) => {
        expect(resp).toEqual({id: 'a2'});
        done();
      });

      http.expectOne('base/prefix/v1/companies/a2').flush({id: 'a2'});

    });

    it('should reduce the state', () => {
      expect(store.onGetOne({...entityStoreInitialState}, {id: '1234', type: 'plant'})).toEqual({
        list: [ {id: '1234', type: 'plant'} as Ent ],
        total: 1,
        selected: {
          id: '1234',
          type: 'plant',
        }
      });

    });

  });

  describe('#findAll', () => {

    it('should get all entities (effect)', (done) => {

      store.findAll({}).subscribe((resp) => {
        expect(resp).toEqual({
          entities: [{id: 'a2'}],
          total: 1,
        });
        done();
      });

      http.expectOne('base/prefix/v1/companies?sort=&count=0').flush({
        entities: [],
        total: 1,
      });

      http.expectOne('base/prefix/v1/companies?sort=&count=1').flush({
        entities: [{id: 'a2'}],
        total: 1,
      });

    });

    it('should reduce the state', () => {
      expect(store.onFindAll({...entityStoreInitialState}, {
        entities: [ {id: '1234', type: 'plant'} as Ent ],
        total: 1,
      })).toEqual({
        list: [ {id: '1234', type: 'plant'} as Ent ],
        total: 1,
      });

    });
  });

  describe('#getPage', () => {

    it('should get a page of entities (effect)', (done) => {

      store.getPage({
        page: 0, count: 10,
      }).subscribe((resp) => {
        expect(resp).toEqual({
          entities: [{id: 1234}],
          total: 1,
          page: 0,
          count: 10,
        });
        done();
      });

      http.expectOne('base/prefix/v1/companies?sort=&count=10&page=1').flush({
        entities: [{id: 1234}],
        total: 1,
      });

    });

    it('should reduce the state', () => {
      expect(store.onGetPage({...entityStoreInitialState}, {
        entities: [ {id: '1234', type: 'plant'} as Ent ],
        total: 1,
        page: 0,
        count: 10,
      })).toEqual({
        list: [ {id: '1234', type: 'plant'} as Ent ],
        total: 1,
        page: 0,
        count: 10,
      });

    });

  });

  describe('#deleteOne', () => {
    beforeEach(() => {
      jest.spyOn(service, 'delete');
    });

    it('should call service', () => {
      store.deleteOne('id');
      expect(service.delete).toHaveBeenCalled();
    });

    it('should reduce state', () => {
      const state = store.onDeleteOne({
        list: [{id: 'rule_id', type: 'animal'}],
        total: 1
      }, {id: 'rule_id' });

      expect(state).toEqual({
        list: [],
        total: 0,
      });
    });

    it('should reduce state many rules', () => {
      const state = store.onDeleteOne({
        list: [ { id: 'id', type: 'animal' }, { id: 'id_1', type: 'plant' } ],
        total: 2
      }, {id: 'id_1'});

      expect(state).toEqual({
        list: [ { id: 'id', type: 'animal' } ],
        total: 1,
      });
    });
  });
});
