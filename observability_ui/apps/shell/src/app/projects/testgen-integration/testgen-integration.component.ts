import { CommonModule } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { takeUntilDestroyed, toObservable, toSignal } from '@angular/core/rxjs-interop';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { ProjectService, TestStatus, parseDate, ProjectStore } from '@observability-ui/core';
import { TranslationModule } from '@observability-ui/translate';
import { InstancesStore } from '../../stores/instances/instances.store';
import { combineLatest, distinctUntilChanged, filter, map, switchMap } from 'rxjs';
import { GetIngrationPipe, HelpLinkComponent, HumanizePipe } from '@observability-ui/ui';
import { TestgenTestType, testTypeHelpLink } from './testgen-integration.model';
import { ChartData, ChartOptions } from 'chart.js';
import { NgChartsModule } from 'ng2-charts';

type ScatterPlotRawPoint = {x: number; y: number; status: TestStatus};

@Component({
  selector: 'shell-testgen-integration',
  templateUrl: 'testgen-integration.component.html',
  styleUrls: [ 'testgen-integration.component.scss' ],
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,

    MatIconModule,
    MatLegacyButtonModule,
    NgChartsModule,

    HelpLinkComponent,
    HumanizePipe,
    GetIngrationPipe,
    TranslationModule,
  ],
})
export class TestgenIntegrationComponent {
  route = inject(ActivatedRoute);
  id = computed(() => this.params()['id']);

  readonly TestStatus = TestStatus;

  private store = inject(InstancesStore);
  private projectStore = inject(ProjectStore);

  test = toSignal(this.projectStore.selectedTest$);
  testLink = computed(() => {
    return testTypeHelpLink[this.test().type as TestgenTestType];
  });
  chart = computed(() => {
    const dateFormatter = new Intl.DateTimeFormat("en-US", {month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric'});
    const currentTest = this.test();
    const occurrences = (this.history() ?? []).filter((test) => !!test.start_time && !!test.metric_value);
    const metricLabel = (currentTest.metric_name || 'Metric Value').replace(/[_-]/g, ' ').toLowerCase().replace(/\b\w/g, s => s.toUpperCase());

    const xTicks = Array.from(occurrences.map((test) => dateFormatter.format(parseDate(test.start_time))));
    const xTicksFromDate = new Map<string, number>();
    const xTicksFromIndex = new Map<number, string>();

    for (const [index, tick] of Object.entries(xTicks)) {
      xTicksFromDate.set(tick, parseInt(index, 10));
      xTicksFromIndex.set(parseInt(index, 10), tick);
    }

    const maxThresholds: {x: number; y: number}[] = [];
    const minThresholds: {x: number; y: number}[] = [];
    for (const [index, test] of occurrences.entries()) {
      if (test.max_threshold) {
        maxThresholds.push({x: index, y: test.max_threshold});
      }
      if (test.min_threshold) {
        minThresholds.push({x: index, y: test.min_threshold});
      }
    }

    const pointColorFromContext = (context: {raw: ScatterPlotRawPoint}) => {
      return {
        [TestStatus.Passed]: '#9CCC65',
        [TestStatus.Warning]: '#FFD54F',
        [TestStatus.Failed]: '#e57373',
      }[context?.raw?.status] ?? '#000000';
    };
    const pointStyleFromContext = (context: {raw: ScatterPlotRawPoint}) => {
      return {
        [TestStatus.Passed]: 'circle',
        [TestStatus.Warning]: 'triangle',
        [TestStatus.Failed]: 'rect',
      }[context?.raw?.status] ?? 'circle';
    };

    return {
      data: {
        datasets: [
          {
            label: 'Maximum',
            data: maxThresholds,
            pointRadius: 0,
            borderDash: [5, 5],
            borderColor: '#000000',
            pointHitRadius: 0,
          },
          {
            label: currentTest.name,
            data: occurrences.map((test, index) => ({
              x: index,
              y: test.metric_value,
              status: test.status
            })),
          },
          {
            label: 'Minimum',
            data: minThresholds,
            pointRadius: 0,
            borderDash: [5, 5],
            borderColor: '#000000',
            pointHitRadius: 0,
          },
        ],
      } as ChartData,
      options: {
        font: {
          family: '"Roboto", "Helvetica Neue", sans-serif',
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            usePointStyle: true,
            backgroundColor: '#616161',
            cornerRadius: 2,
            callbacks: {
              title: (items) => {
                return xTicks[items[0].parsed.x];
              },
              label: (context) => {
                return `${metricLabel}: ${context.parsed.y}`;
              },
            },
          },
        },
        scales: {
          x: {
            ticks: {
              callback: (value) => {
                return xTicks[value as number];
              },
            },
            grid: {
              display: false,
            },
          },
          y: {
            title: {
              text: metricLabel,
              display: true,
              align: 'end',
            },
            grid: {
              display: false,
            },
          },
        },
        datasets: {
          scatter: {
            showLine: true,
            borderWidth: 1,
            borderColor: '#9E9E9E',
            pointBorderColor: pointColorFromContext,
            pointBackgroundColor: pointColorFromContext,
          },
        },
        elements: {
          point: {
            radius: 4,
            pointStyle: pointStyleFromContext,
          },
        },
      } as ChartOptions,
    };
  });

  private history = toSignal(
    combineLatest([
      toObservable(this.test),
      this.route.parent.parent.params,
    ]).pipe(
      filter(([test,]) => !!test),
      switchMap(([test, {projectId}]) => this.projectService.getTests({ parentId: projectId, filters: {key: test.key}, sort: 'desc', sort_by: 'start_time', count: 20 })),
      map((response) => response.entities.reverse()),
    )
  );

  private params = toSignal(this.route.parent.params);
  private projectService = inject(ProjectService);

  constructor() {
    this.route.parent.params.pipe(
      map((params) => params['testId'] as string),
      filter((testId) => !!testId),
      distinctUntilChanged(),
    ).pipe(
      takeUntilDestroyed(),
    ).subscribe((testId) => {
      this.projectStore.dispatch('selectTest', testId);
    });
  }
}
