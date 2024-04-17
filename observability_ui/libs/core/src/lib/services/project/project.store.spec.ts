import { TestBed } from '@angular/core/testing';
import { ProjectStore, State } from './project.store';
import { ProjectService } from './project.service';
import { ConfigService } from '../../config/config.service';
import { PaginatedRequest } from '../../entity';
import { of } from 'rxjs';
import { EventType } from '../../models/event.model';
import { Project } from './project.model';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('project.store', () => {
  let store: ProjectStore;
  let projectService: ProjectService;

  const projects = [
    { id: 'p1' } as Project,
    { id: 'p2' } as Project,
  ];

  const tests = [ { id: 'test-id-1', name: 'test 1' }, { id: 'test-id-2', name: 'test 2' } ];

  const initialState = {
    events: {
      list: [ { id: 'a' }, { id: 'b' } ] as EventType[],
      total: 2,
    },
    list: [],
    total: 0,
  } as unknown as State;

  let testScheduler: TestScheduler;

  beforeEach(() => {
    testScheduler = new TestScheduler();

    TestBed.configureTestingModule({
      providers: [
        ProjectStore,
        MockProvider(ConfigService, class {
          get = () => 'base_url';
        }),
        MockProvider(ProjectService, class {
          // overrides
          getEvents = () => of({ entities: [], total: 0 });
          getOne = (pId: string) => of(projects.find(({ id }) => id === pId));
        })
      ],
    });

    projectService = TestBed.inject(ProjectService);
    store = TestBed.inject(ProjectStore);

    projectService.getTestById = jest.fn().mockReturnValue(of(tests[1]));
  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

  describe('#projectChanged', () => {
    it('should start with false', () => {
      testScheduler.expect$(store.projectChanged$).toBe('a', {
        a: false
      });
    });

    it('should not count first change', () => {
      testScheduler.run(({}) => {
        store.dispatch('getOne', 'p2');

        TestScheduler.expect$(store.projectChanged$).toBe('a', {
          a: false,
        });
      });
    });


    // testing the observable per se is problematic and convoluted
    // proceeding testing private methods instead
    describe('reduceBuffer', () => {

      it('should shift a cap sized (2) array with the current selected project', () => {

        expect(store['reduceBuffer'](
            [ undefined, undefined ], projects[0]
          )
        ).toEqual([ undefined, projects[0] ]);

        expect(store['reduceBuffer'](
            [ undefined, projects[0] as Project ], projects[1]
          )
        ).toEqual([ projects[0], projects[1] ]);

        expect(store['reduceBuffer'](
          [ projects[0], projects[1] ], projects[1]
          )
        ).toEqual([ projects[1], projects[1] ]);

      });

    });

    // proceeding testing private methods instead
    describe('projectChanged', () => {
      it('should return true when project changes', () => {
        expect(store['projectChanged'](projects[0], projects[1])).toBeTruthy();

        expect(store['projectChanged'](projects[1], projects[0])).toBeTruthy();
        expect(store['projectChanged'](projects[1], undefined)).toBeTruthy();
      });

      it('should return false when it first change or project does not changes', () => {

        expect(store['projectChanged'](undefined, projects[0])).toBeFalsy();
        expect(store['projectChanged'](projects[0], projects[0])).toBeFalsy();
      });


    });

  });

  describe('@getOne', () => {

    describe('when selected project changes', () => {

      it('should reset events list', () => {
        expect(
          store.onGetOne(initialState, {
            id: 'project-id-2'
          } as Project)
        ).toEqual(expect.objectContaining({
          events: {
            list: [],
            total: 0,
          }
        }));
      });

    });


  });

  describe('@getEventsByPage', () => {

    it('should call the service', () => {

      new TestScheduler().expect$(store.getEventsByPage({} as PaginatedRequest)).toContain({
        entities: [],
        total: 0
      });

    });

    it('should set state', () => {

      const state = store.onGetEventsByPage(initialState, {
        entities: [ { id: 'c' }, { id: 'd' } ] as EventType[],
        total: 2,
      });

      expect(state).toEqual(expect.objectContaining({
        events: {
          list: [ { id: 'c' }, { id: 'd' } ] as EventType[],
          total: 2,
        }
      }));

    });
  });

  describe('@createOne', () => {

    it('should add created entity to the `list`', () => {


      const state = store.onCreateOne(initialState, {
        id: 'project-id-new'
      } as Project);


      expect(state.list.length).toEqual(initialState.list.length + 1);
      expect(state.total).toEqual(initialState.total + 1);

    });
  });

  describe('@findAll', () => {

    describe('setting selected project', () => {

      it('should leave selected project if already set', () => {

        const state = store.onFindAll({
          ...initialState,
          selected: { id: 'project-id' } as Project
        }, {
          entities: [ { id: '1' }, { id: '2' } ] as Project[],
          total: 2,
        });

        expect(state.selected).toEqual({ id: 'project-id' });

      });

      it('should look for a project named default if no project has been selected yet already set', () => {

        const state = store.onFindAll(initialState, {
          entities: [ { id: '1' }, { id: '2' }, { id: '3', name: 'default' } ] as Project[],
          total: 2,
        });

        expect(state.selected).toEqual({ id: '3', name: 'default' });

      });

      it('should get the first project in the list if no project has been selected yet already set and no project name `default` can be found', () => {

        const state = store.onFindAll(initialState, {
          entities: [ { id: '1' }, { id: '2' }, { id: '3' } ] as Project[],
          total: 2,
        });

        expect(state.selected).toEqual({ id: '1' });

      });
    });
  });

  describe('selectTest()', () => {
    it('should fetch the selected test', () => {
      store.dispatch('selectTest', 'test-id-2');
      expect(projectService.getTestById).toBeCalledWith('test-id-2');
    });

    it('should set the fetched test as selected', () => {
      store.dispatch('selectTest', 'test-id-2');
      new TestScheduler().expect$(store.state$).toContain(expect.objectContaining({
        selectedTest: tests[1]
      }));
    });
  });
});
