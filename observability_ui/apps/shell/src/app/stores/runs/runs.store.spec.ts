import { TestBed } from '@angular/core/testing';
import { RunsStore } from './runs.store';
import { ProjectRunsService } from '../../services/project-runs/project-runs.service';
import { MockProvider } from 'ng-mocks';
import { of } from 'rxjs';
import { ProjectService } from '@observability-ui/core';

describe('runs.store', () => {
  let store: RunsStore;
  let projectService: ProjectService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RunsStore,
        MockProvider(ProjectRunsService, {
          findAll: jest.fn().mockReturnValue(of({ entities: [] })),
        }),
        MockProvider(ProjectService, {
          getTests: jest.fn()
        })
      ],
    });

    store = TestBed.inject(RunsStore);
    projectService = TestBed.inject(ProjectService);
  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

  describe('getTestsByPage', () => {
    it('should call projectService.getTests with the paginated request', () => {
      store.dispatch('getTestsByPage', 'id', {} as any);
      expect(projectService.getTests).toHaveBeenCalledWith({ parentId: 'id' });
    });
  });
});
