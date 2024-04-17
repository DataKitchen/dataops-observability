import { Component, computed, Input } from '@angular/core';
import { InstanceRunSummary } from '@observability-ui/core';
import { RunProcessedStatus, sortByStatusWeight } from '@observability-ui/core';

@Component({
  selector: 'shell-instance-runs-summary',
  templateUrl: 'instance-runs-summary.component.html',
  styleUrls: [ 'instance-runs-summary.component.scss' ]
})

export class InstanceRunsSummaryComponent {
  @Input() summaries: InstanceRunSummary[];

  sortedSummaries = computed(() => sortByStatusWeight(this.summaries));

  protected readonly RunProcessedStatus = RunProcessedStatus;
}
