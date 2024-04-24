import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DotsChartComponent } from './dots-chart.component';

describe('DotsChartComponent', () => {
  let fixture: ComponentFixture<DotsChartComponent>;
  let component: DotsChartComponent;

  const dots = [
    {
      template: undefined,
      value: {
        id: '1',
        project: {
          id: '1',
          name: 'Project A'
        },
        journey: {
          id: '2',
          name: 'Journey A'
        },
      },
    },
    {
      template: undefined,
      value: {
        id: '2',
        project: {
          id: '1',
          name: 'Project A'
        },
        journey: {
          id: '2',
          name: 'Journey A'
        },
      },
    },
    {
      template: undefined,
      value: {
        id: '3',
        project: {
          id: '1',
          name: 'Project A'
        },
        journey: {
          id: '5',
          name: 'Journey B'
        },
      },
    },
    {
      template: undefined,
      value: {
        id: '4',
        project: {
          id: '2',
          name: 'Project B'
        },
        journey: {
          id: '6',
          name: 'Journey C'
        },
      },
    },
  ] as any[];

  beforeEach(async () => {

    TestBed.configureTestingModule({
      imports: [
        DotsChartComponent,
      ],
    });

    fixture = TestBed.createComponent(DotsChartComponent);
    component = fixture.componentInstance;

    component.levels = [
      {groupByField: 'project.id', labelField: 'project.name', linkField: () => '/link/to/project'},
      {groupByField: 'journey.id', labelField: 'journey.name', linkField: () => '/link/to/journey'},
    ];

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });

  describe('toggleExpand()', () => {
    beforeEach(() => {
      const grouped = component['groupDots'](dots as any, component.levels[0], 0);
      component.groups.mutate((currentGroups) => {
        for (const group of grouped) {
          currentGroups.set(group.id, group);
        }
      });
    });

    it('should set the group expanded', () => {
      const groups = Array.from(component.groups().values());

      component.toggleExpand(groups[0]);
      expect(groups[0].expanded).toBeTruthy();
    });

    it('should set the group children', () => {
      const groups = Array.from(component.groups().values());

      component.toggleExpand(groups[0]);
      expect(groups[0].children.length).toBe(2);
    });
  });

  describe('closeExternalExpandedGroup()', () => {
    it('should set the external expanded group to undefined', () => {
      component.expandedExternalGroup.set({} as any);
      component.closeExternalExpandedGroup();
      expect(component.expandedExternalGroup()).toBeUndefined();
    });
  });
});
