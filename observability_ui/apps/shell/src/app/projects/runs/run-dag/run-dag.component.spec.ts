import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { parseDate, RunTask } from '@observability-ui/core';
import { DagComponent, DagEdgeDirective, DagNodeDirective } from '@observability-ui/ui';
import { MockComponent, MockDirectives, MockProvider } from 'ng-mocks';
import { of } from 'rxjs';
import { RunTasksStore } from '../../../stores/run-tasks/run-tasks.store';
import { RunDagComponent } from './run-dag.component';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { MatIcon } from '@angular/material/icon';
import { RunsStore } from '../../../stores/runs/runs.store';

describe('RunDagComponent', () => {
  const runId = 'f4dd48b3-a6da-497a-be1a-c9dd8e9d1efc';
  const tasks = [
    {
      "id": "d7596eed-f1b5-43e6-9600-7df237b9555f",
      "run": runId,
      "start_time": "2022-08-29T12:44:22",
      "end_time": "2022-08-29T13:00:12",
      "task": {
        "id": "6d8a2961-1078-4c67-acf7-e007e93c7e0e",
        "key": "Task A"
      }
    },
    {
      "id": "600332d8-16a6-4640-9d28-711460443089",
      "run": runId,
      "start_time": "2022-08-29T12:47:27",
      "end_time": "2022-08-29T13:40:26",
      "task": {
        "id": "6f27f582-b242-432c-ba9c-6c040da89ab2",
        "key": "Task B"
      }
    },
    {
      "id": "27b1cfe1-881c-4cfc-92af-26edb9798810",
      "run": runId,
      "start_time": "2022-08-29T13:01:10",
      "end_time": "2022-08-29T13:04:33",
      "task": {
        "id": "05778977-a97a-4ce4-b2d3-520c162e76c0",
        "key": "Task C"
      }
    },
    {
      "id": "9f40e480-3550-4638-9e31-8faebaf579e4",
      "run": runId,
      "start_time": "2022-08-29T13:06:21",
      "end_time": "2022-08-29T13:13:40",
      "task": {
        "id": "58e1e4ee-762a-4305-af8b-1f849f61bec8",
        "key": "Task D"
      }
    },
    {
      "id": "76ce64d2-41a1-491a-a2bf-3314e690e863",
      "run": runId,
      "start_time": "2022-08-29T13:06:36",
      "end_time": "2022-08-29T13:30:17",
      "task": {
        "id": "11a545f5-6151-4f3a-93ce-699459b2209b",
        "key": "Task E"
      }
    },
    {
      "id": "fe0b221a-8170-4616-87cd-79c69d511b5f",
      "run": runId,
      "start_time": "2022-08-29T13:20:56",
      "end_time": "2022-08-29T13:43:17",
      "task": {
        "id": "0bcb3e93-586e-44ed-9b5f-29106a9e7b16",
        "key": "Task F"
      }
    }
  ] as RunTask[];
  const parsedTasks = tasks.map(t => ({ ...t, start_time: parseDate(t.start_time)!, end_time: parseDate(t.end_time as string)! }));

  let runTasksStore: RunTasksStore;
  let runsStore: RunsStore;

  let fixture: ComponentFixture<RunDagComponent>;
  let component: RunDagComponent;

  beforeEach(() => {

    TestBed.configureTestingModule({
      declarations: [
        MockComponent(DagComponent),
        MockComponent(MatIcon),
        MockDirectives(
          DagEdgeDirective,
          DagNodeDirective,

        ),
        RunDagComponent,
      ],
      providers: [
        MockProvider(RunTasksStore, {
          list$: of(tasks),
          getLoadingFor: jest.fn(),
          dispatch: jest.fn()
        }),
        MockProvider(RunsStore, {
          dispatch: jest.fn()
        }),
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {}, ActivatedRouteMock({ runId })),
        }
      ],
    });

    runTasksStore = TestBed.inject(RunTasksStore);
    runsStore = TestBed.inject(RunsStore);

    fixture = TestBed.createComponent(RunDagComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit()', () => {
    beforeEach(() => {

      fixture.detectChanges();
    });

    it('should initially get all the tasks', () => {
      expect(runTasksStore.dispatch).toBeCalledWith('findAll', { parentId: runId });
    });

    it('should refresh header details', () => {
      expect(runsStore.dispatch).toBeCalledWith('getOne', runId);
    });
  });

  describe('linkTasks()', () => {
    const taskA = parsedTasks[0];
    const taskB = parsedTasks[1];
    const taskC = parsedTasks[2];
    const taskD = parsedTasks[3];
    const taskE = parsedTasks[4];
    const taskF = parsedTasks[5];

    it('should have no edges for a single node', () => {
      const edges = component.linkTasks([ taskA ]);
      expect(edges.length).toBe(0);
    });

    it('should link Task A to Task C', () => {
      const edges = component.linkTasks(parsedTasks);
      expect(edges).toContainEqual(expect.objectContaining({ from: taskA.id, to: taskC.id }));
    });

    it('should link Task C to Task D', () => {
      const edges = component.linkTasks(parsedTasks);
      expect(edges).toContainEqual(expect.objectContaining({ from: taskC.id, to: taskD.id }));
    });

    it('should link Task C to Task E', () => {
      const edges = component.linkTasks(parsedTasks);
      expect(edges).toContainEqual(expect.objectContaining({ from: taskC.id, to: taskE.id }));
    });

    it('should not link Task C to Task F', () => {
      const edges = component.linkTasks(parsedTasks);
      expect(edges).not.toContainEqual(expect.objectContaining({ from: taskC.id, to: taskF.id }));
    });

    it('should link Task D to Task F', () => {
      const edges = component.linkTasks(parsedTasks);
      expect(edges).toContainEqual(expect.objectContaining({ from: taskD.id, to: taskF.id }));
    });

    it('should not link from/to B', () => {
      const edges = component.linkTasks(parsedTasks);
      const allTasks = edges.reduce((all, edge) => [ ...all, edge.from, edge.to ], [] as string[]);
      expect(allTasks).not.toContain(taskB.id);
    });

    it('should link tasks with where start of A = start of B', () => {
      const edges = component.linkTasks([ taskA, { ...taskB, start_time: taskA.end_time as Date }]);
      expect(edges).toContainEqual(expect.objectContaining({ from: taskA.id, to: taskB.id }));
    });

    it('should not link a task to itself', () => {
      const edges = component.linkTasks([ taskA, { ...taskC, end_time: taskC.start_time }]);
      expect(edges).not.toContainEqual(expect.objectContaining({ from: taskC.id, to: taskC.id }));
    });
  });

});
