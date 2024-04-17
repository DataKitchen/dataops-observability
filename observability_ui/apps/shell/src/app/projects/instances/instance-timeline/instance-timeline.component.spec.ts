import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InstanceTimelineComponent } from './instance-timeline.component';
import { of } from 'rxjs';
import { MockComponents, MockDirective } from 'ng-mocks';
import { ActivatedRoute } from '@angular/router';
import { MatCard, MatCardContent } from '@angular/material/card';
import { MatSpinner } from '@angular/material/progress-spinner';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { GanttChartModule } from '@observability-ui/ui';
import { ProjectStore } from '@observability-ui/core';
import { ActivatedRouteMock, MockProvider, Mocked } from '@datakitchen/ngx-toolkit';

describe('InstanceTimelineComponent', () => {
  const instanceId = '123';
  const projectId = 'abc';

  let instanceStore: Mocked<InstancesStore>;

  let component: InstanceTimelineComponent;
  let fixture: ComponentFixture<InstanceTimelineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InstanceTimelineComponent, MockComponents(MatCard, MatSpinner), MockDirective(MatCardContent) ],
      imports: [
        GanttChartModule,
      ],
      providers: [
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {},
              ActivatedRouteMock({ id: instanceId })
            )
        },
        MockProvider(InstancesStore, class {
          runs$ = of([]);
        }),
        MockProvider(ProjectStore, class {
          current$ = of({id: projectId});
        }),
      ]
    }).compileComponents();

    instanceStore = TestBed.inject(InstancesStore) as Mocked<InstancesStore>;

    fixture = TestBed.createComponent(InstanceTimelineComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should fetch batch runs for timeline', () => {
    expect(instanceStore.dispatch).toBeCalledWith('findAllBachRuns', projectId, instanceId);
  });

  it('should refresh header details', () => {
    expect(instanceStore.dispatch).toBeCalledWith('getOne', instanceId);
  });
});
