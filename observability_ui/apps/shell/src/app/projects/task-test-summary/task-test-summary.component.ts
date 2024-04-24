import { Component, computed, Input, signal } from '@angular/core';
import { getCompleteSummary } from './task-test-summary.utils';
import { RunTaskSummary, sortByStatusWeight, TestSummary } from '@observability-ui/core';
import { CommonModule } from '@angular/common';
import { DkTooltipModule } from '@observability-ui/ui';
import { TranslationModule } from '@observability-ui/translate';

@Component({
  selector: 'shell-task-test-summary',
  templateUrl: 'task-test-summary.component.html',
  styleUrls: [ 'task-test-summary.component.scss' ],
  imports: [
    CommonModule,
    DkTooltipModule,
    TranslationModule,
  ],
  standalone: true,
})
export class TaskTestSummaryComponent {

  @Input() set tasksSummaries(value: RunTaskSummary[]) {
    this._tasksSummaries.set(value);
  }
  @Input() set testsSummaries(value: TestSummary[]) {
    this._testsSummaries.set(value);
  }
  @Input() showLabels: boolean = true;

  sortedTasksSummary = computed(() => sortByStatusWeight(this._tasksSummaries()));
  sortedTestsSummary = computed(() => sortByStatusWeight(this._testsSummaries()));

  tasksSummaryAggregate = computed(() => getCompleteSummary(this._tasksSummaries() as any));
  testsSummaryAggregate = computed(() => getCompleteSummary<TestSummary>(this._testsSummaries()));

  private _tasksSummaries = signal<RunTaskSummary[]>([]);
  private _testsSummaries = signal<TestSummary[]>([]);
}
