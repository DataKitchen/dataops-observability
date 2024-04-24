import { Injectable } from "@angular/core";
import { EntityStore } from "../entity";
import { OrganizationService, ProjectService, UserService } from "../services";
import { TestBed } from "@angular/core/testing";
import { MockProviders } from "ng-mocks";
import { resetStores } from './reset-stores.guard';

describe('Reset Stores Guard Fn', () => {
  @Injectable()
  class StoreA extends EntityStore<any, any> {
    constructor(protected service: ProjectService) {
      super({ list: [] });
    }
  
    override dispatch = jest.fn();
  }

  @Injectable()
  class StoreB extends EntityStore<any, any> {
    constructor(protected service: OrganizationService) {
      super({ list: [] });
    }

    override dispatch = jest.fn();
  }

  @Injectable()
  class StoreC extends EntityStore<any, any> {
    constructor(protected service: UserService) {
      super({ list: [] });
    }

    override dispatch = jest.fn();
  }

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        MockProviders(ProjectService, OrganizationService, UserService),
        StoreA,
        StoreB,
        StoreC,
      ],
    });
  });

  it('should dispatch the reset action for each passed store', () => {
    const a = TestBed.inject(StoreA);
    const c = TestBed.inject(StoreA);

    TestBed.runInInjectionContext(resetStores(StoreA, StoreC) as () => boolean);
    expect(a.dispatch).toBeCalledWith('reset');
    expect(c.dispatch).toBeCalledWith('reset');
  });

  it('should NOT dispatch the reset action for stores not passed as argument', () => {
    const b = TestBed.inject(StoreB);

    TestBed.runInInjectionContext(resetStores(StoreA, StoreC) as () => boolean);
    expect(b.dispatch).not.toBeCalledWith('reset');
  });
});
